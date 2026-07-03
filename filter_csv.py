#!/usr/bin/env python3
"""Remove rows whose url is a government site, a directory/association, or social media."""
import csv
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
CSV_PATH = ROOT / "ab_combined.csv"

BLOCKED_DOMAINS = {
    # government
    "albertahealthservices.ca", "prl.ab.ca", "ualberta.ca", "atb.com", "canada.ca",
    "falher.ca", "foremost.shortgrass.ca", "foremostagencies.ca", "foremostalberta.com",
    "girouxville.ca", "nobleford.ca", "stavely.ca", "westlock.ca", "bonaccord.ca",
    "athabasca.ca", "khs.btps.ca",
    # directories / associations
    "albertadentalassociation.ca", "dentaltown.ca", "abrda.ca", "cdsab.ca", "camrosedirectory.ca",
    # social media
    "facebook.com", "m.facebook.com", "instagram.com", "fb.com",
    # finance / insurance
    "sunlife.ca", "luminohealth.sunlife.ca", "westernfinancialgroup.ca", "dyckinsurance.ca",
    "awarefinancial.ca", "stoneins.ca",
    # veterinary / pet
    "ardrossanvet.ca", "aspentrailsveterinaryclinic.com", "bearcreekanimalclinic.ca",
    "beaumontanimalclinicab.com", "beaverhillveterinaryservices.ca", "bigrockanimalclinic.com",
    "blackfaldsvet.ca", "bowrivervet.com", "camroseanimalshelter.ca", "canmorevet.com",
    "carstairsveterinaryclinic.com", "centralvetclinic.ca", "cityvetsairdrie.ca", "coaldalepet.com",
    "cochraneanimalclinic.com", "cypressviewvet.ca", "deerparkpet.ca", "diamondvalleyvet.ca",
    "foothillsveterinaryclinic.com", "fortmacleodveterinaryclinic.ca", "hilltopvet.com",
    "lacombeveterinarycentre.com", "leducanimalclinic.com", "manningvet.ca", "mypetneeds.ca",
    "northernpetemporium.ca", "parkveterinarycentre.com", "pawpetual-friends.square.site",
    "pinchercreekvetclinic.ca", "pipercreekvet.com", "ponokavet.ca", "prairierosevet.ca",
    "pulseveterinary.ca", "rangeroadvet.com", "sangudoveterinaryclinic.com", "stalbertanimalclinic.com",
    "stettlervetclinic.com", "stonyplainvetclinic.com", "store.petvalu.ca", "sturgeoncountykennels.ca",
    "thelittlepetcompany.ca", "thrivevetcare.ca", "valleyvetdrum.ca", "vulcanvet.ca",
    "westlockvetcenter.com", "wetaskiwinvet.ca", "whitecourtvet.com", "wiseequinevet.com",
    "petsmart.ca", "boneandbiscuit.ca", "cochranehumane.ca", "summitdoestraining.ca",
    # pharmacy
    "alixdrugs.ca", "bonaccordpharmacy.ca", "bookmypharmacy.com", "guardian-ida-remedysrx.ca",
    "mayjoradpharmacies.com", "medicineshoppe.ca", "noblefordpharmacy.ca", "pharmachoice.com",
    "pharmasave.com", "rexall.ca", "shoppersdrugmart.ca", "thecommonspharmacy.com",
    "wembleypharmacy.ca", "medigroup.ca",
    # physio / chiro
    "backcountrychiro.ca", "bowriverchiropractic.ca", "coaldalechiropractic.com", "deutscherchiro.com",
    "grimshawchiros.com", "medicinehatphysio.ca", "peaceriverphysiotherapy.com", "pembinaphysio.com",
    "prestigephysio.ca", "riversidephysio.net", "stalbertphysiotherapy.com", "thorsbychiropractic.com",
    "westlockchiro.ca",
    # eye / vision
    "acuityeyecare.ca", "airdriefamilyeyedoctors.com", "eyedoctors.pearlevision.com",
    "sherwoodparkoptometry.ca", "specsavers.ca", "sturgeonvisioncentre.com", "visionaryeyecentre.com",
    # medical / health / PCN
    "arrowwoodmedical.ca", "ccdclinic.com", "consortmedicalclinic.com", "crossfieldclinic.com",
    "delburnemedical.ca", "falhermedicalclinic.com", "glacierchc.org", "goldenhealthgroup.com",
    "hardinmedicalclinic.ca", "healthfirstclinic.ca", "lbdpcn.com", "lethbridgesleepclinic.ca",
    "lifelinemedicalclinic.ca", "manningmedical.com", "mlchc.org", "northwestpcn.ca",
    "oasismedicalclinic.ca", "palliserpcn.ca", "re-zenmedicalesthetics.ca", "reddeerpcn.com",
    "riversidemedical.ca", "sherwoodparkpcn.com", "smithclinic.net", "stadekclinic.ca",
    "vulcanclinic.ca", "westviewpcn.ca", "radiushealth.ca", "prairiefamilyhealth.ca",
    "milletmc.inputhealth.com", "totalhealthineckville.com", "six08health.com", "opalcare.ca",
    "pihealth.ca", "doctorsplus.ca", "childrenfirstedmonton.com", "collegiatesportsmedicine.ca",
    # beauty / spa / wellness
    "altitudespa.ca", "applewellnesscenter.com", "auroraskin.ca", "bellaesthetics.ca",
    "dugganwellnesscentre.ca", "limebeauty.ca", "mmccosmeticlaser.com", "modernaesthetics.ca",
    "optimumwellnesscentres.com", "purelifewellness.janeapp.com", "rtisticbeautyaesthetics.ca",
    "saltwaterwellnesscentre.com", "synergywellnesscentre.ca", "theassemblywellness.com",
    "urbanaestheticsyxh.com",
    # hotel / restaurant / retail / gas / misc commerce
    "alixinn.com", "barkstmarket.ca", "bashawmeats.com", "canadiantire.ca", "car-wash-laundromat.jany.io",
    "carselandrestaurant.com", "cedar-villa-motel.com.es", "dominos.ca", "elkwaterlakelodge.com",
    "fields.ca", "find.shell.com", "freson.com", "frontierlodge.ca", "goldenprairielodge.com",
    "hillsofhomecafe.twupro.com", "homehardware.ca", "hotelni.com", "lakelouiseliquor.com",
    "lakelouisevillagegrill.ca", "milohotel.ca", "noblefordautorepair.com", "nofrills.ca",
    "norsemeninn.com", "pinecreekmotel.com", "realcanadiansuperstore.ca", "redapplestores.com",
    "sobeys.com", "the-method-2381.myshopify.com", "thorsbyfamilyrestaurant.com", "tirecraftforemost.ca",
    "vauxhallmeats.com", "whistlestoptruckstop.ca", "wyndhamhotels.com", "bestwestern.com",
    "heidishaus.com", "kegriver.com", "local.bumpertobumper.ca", "luigiscremona.ca", "mymenuweb.com",
    "plamondoncoop.ca", "rrsharpening.ca", "sawridgetravelcentre.com", "thebabyfootprint.com",
    "thebakedery.biz", "peterpondmall.com",
    # finance / legal / realty
    "branches.fairstone.ca", "brokerlink.ca", "kowalrealty.ca", "locations.moneygram.com",
    "moneygram.com", "sandstonelaw.ca",
    # schools / libraries / municipal / misc institutions
    "afsc.ca", "altario.plrd.ab.ca", "atcfn.ca", "beisekerregistry.com", "centralalbertaco-op.crs",
    "chipewyanlakeschool.ca", "co-op.crs", "coaldalelibrary.ca", "cornerstoneco-op.crs",
    "couttslibrary.ca", "deboltlibrary.ab.ca", "heinsburgschool.ca", "kinusolibrary.ab.ca",
    "mundarelibrary.ab.ca", "mundareregistry.ca", "nait.ca", "newhorizonco-op.crs",
    "northcorridorco-op.crs", "rcmp-grc.gc.ca", "servicecanada.gc.ca", "southcountryco-op.crs",
    "stavelylibrary.ca", "thorsbymunicipallibrary.ab.ca", "townshipdwg.ca", "trochulibrary.ca",
    "villageofarrowwood.ca", "villageofbawlf.com", "villageofempress.com", "khs.btps.ca",
    "gopherholemuseum.org", "lacretemuseum.weebly.com", "livingwateredu.com",
    "bibstobookbagschildcarecentre.com", "fivemilehallcatering.ca", "prestigeprintingandsigns.ca",
    "connelly-mckinley.com", "melcor.ca", "innisfree.ca", "bashawsports.com",
    # further confirmed junk (2nd deep pass)
    "acera.ca", "agfoods.com", "agroplus.ca", "alixcrc.com", "canadapost.ca", "ceda.com",
    "covenanthealth.ca", "duchessvillagesuites.com", "externalaffairs.ca", "fhfd.ca", "fmspca.ca",
    "fortmckay.com", "horizoncosmetic.ca", "karuna.dhamma.org", "ldsanctuary.com", "ldss.ca",
    "petro-canada.ca", "ranchdocs.com", "rivercitycentre.ca", "rxellence.ca",
    "sabir.organicbaghbani.com", "southpointairdrie.com", "thebethanygroup.ca", "tripca.cyou",
    "trochuarb.ca", "couleekids.com", "allenbrentwood.com",
}


def domain_of(url):
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    kept = []
    removed = []
    for row in rows:
        url = (row.get("url") or "").strip()
        if domain_of(url) in BLOCKED_DOMAINS:
            removed.append(row)
        else:
            kept.append(row)

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept)

    print(f"Rows before: {len(rows)}")
    print(f"Rows after:  {len(kept)}")
    print(f"Removed:     {len(removed)}")
    print()
    print("Removed rows by domain:")
    from collections import Counter
    c = Counter(domain_of((r.get('url') or '')) for r in removed)
    for domain, count in c.most_common():
        print(f"  {count:3d}  {domain}")


if __name__ == "__main__":
    main()
