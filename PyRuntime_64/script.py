import os
import re
import sys
import json
import time
import random
import hashlib
from pathlib import Path
from io import BytesIO
from typing import Dict, Optional, Tuple
from functools import wraps

try:
    import httpx
except ImportError:
    print("Kesalahan: httpx diperlukan. Install: pip install httpx")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Kesalahan: Pillow diperlukan. Install: pip install Pillow")
    sys.exit(1)


# ============ KONFIGURASI ============
PROGRAM_ID = "67c8c14f5f17a83b745e3f82"
SHEERID_API_URL = "https://services.sheerid.com/rest/v2"
MIN_DELAY = 300
MAX_DELAY = 800


# ============ PELACAKAN STATISTIK ============
class Stats:
    """Melacak tingkat keberhasilan berdasarkan organisasi"""
    
    def __init__(self):
        self.file = Path(__file__).parent / "stats.json"
        self.data = self._load()
    
    def _load(self) -> Dict:
        if self.file.exists():
            try:
                return json.loads(self.file.read_text())
            except:
                pass
        return {"total": 0, "success": 0, "failed": 0, "orgs": {}}
    
    def _save(self):
        self.file.write_text(json.dumps(self.data, indent=2))
    
    def record(self, org: str, success: bool):
        self.data["total"] += 1
        if success:
            self.data["success"] += 1
        else:
            self.data["failed"] += 1
        
        if org not in self.data["orgs"]:
            self.data["orgs"][org] = {"success": 0, "failed": 0}
        
        if success:
            self.data["orgs"][org]["success"] += 1
        else:
            self.data["orgs"][org]["failed"] += 1
        self._save()
    
    def get_rate(self, org: str = None) -> float:
        if org:
            o = self.data["orgs"].get(org, {})
            total = o.get("success", 0) + o.get("failed", 0)
            if total == 0:
                return 50.0
            return (o.get("success", 0) / total * 100) if total else 50.0
        
        total = self.data.get("total", 0)
        if total == 0:
            return 0.0
        return (self.data.get("success", 0) / total * 100) if total else 0.0
    
    def print_stats(self):
        print("\nStatistik:")
        print(f"   Total: {self.data['total']} | Berhasil: {self.data['success']} | Gagal: {self.data['failed']}")
        if self.data["total"]:
            print(f"   Tingkat Keberhasilan: {self.get_rate():.1f}%")


stats = Stats()


# ============ UNIVERSITAS DENGAN BOBOT ============
UNIVERSITIES = [
    # =========== AS - PRIORITAS TINGGI ===========
    {"id": 2565, "name": "Pennsylvania State University-Main Campus", "domain": "psu.edu", "weight": 100},
    {"id": 3499, "name": "University of California, Los Angeles", "domain": "ucla.edu", "weight": 98},
    {"id": 3491, "name": "University of California, Berkeley", "domain": "berkeley.edu", "weight": 97},
    {"id": 1953, "name": "Massachusetts Institute of Technology", "domain": "mit.edu", "weight": 95},
    {"id": 3113, "name": "Stanford University", "domain": "stanford.edu", "weight": 95},
    {"id": 2285, "name": "New York University", "domain": "nyu.edu", "weight": 96},
    {"id": 1426, "name": "Harvard University", "domain": "harvard.edu", "weight": 92},
    {"id": 590759, "name": "Yale University", "domain": "yale.edu", "weight": 90},
    {"id": 2626, "name": "Princeton University", "domain": "princeton.edu", "weight": 90},
    {"id": 698, "name": "Columbia University", "domain": "columbia.edu", "weight": 92},
    {"id": 3508, "name": "University of Chicago", "domain": "uchicago.edu", "weight": 88},
    {"id": 943, "name": "Duke University", "domain": "duke.edu", "weight": 88},
    {"id": 751, "name": "Cornell University", "domain": "cornell.edu", "weight": 90},
    {"id": 2420, "name": "Northwestern University", "domain": "northwestern.edu", "weight": 88},
    {"id": 3568, "name": "University of Michigan", "domain": "umich.edu", "weight": 95},
    {"id": 3686, "name": "University of Texas at Austin", "domain": "utexas.edu", "weight": 94},
    {"id": 1217, "name": "Georgia Institute of Technology", "domain": "gatech.edu", "weight": 93},
    {"id": 602, "name": "Carnegie Mellon University", "domain": "cmu.edu", "weight": 92},
    {"id": 3477, "name": "University of California, San Diego", "domain": "ucsd.edu", "weight": 93},
    {"id": 3600, "name": "University of North Carolina at Chapel Hill", "domain": "unc.edu", "weight": 90},
    {"id": 3645, "name": "University of Southern California", "domain": "usc.edu", "weight": 91},
    {"id": 3629, "name": "University of Pennsylvania", "domain": "upenn.edu", "weight": 90},
    {"id": 1603, "name": "Indiana University Bloomington", "domain": "iu.edu", "weight": 88},
    {"id": 2506, "name": "Ohio State University", "domain": "osu.edu", "weight": 90},
    {"id": 2700, "name": "Purdue University", "domain": "purdue.edu", "weight": 89},
    {"id": 3761, "name": "University of Washington", "domain": "uw.edu", "weight": 90},
    {"id": 3770, "name": "University of Wisconsin-Madison", "domain": "wisc.edu", "weight": 88},
    {"id": 3562, "name": "University of Maryland", "domain": "umd.edu", "weight": 87},
    {"id": 519, "name": "Boston University", "domain": "bu.edu", "weight": 86},
    {"id": 378, "name": "Arizona State University", "domain": "asu.edu", "weight": 92},
    {"id": 3521, "name": "University of Florida", "domain": "ufl.edu", "weight": 90},
    {"id": 3535, "name": "University of Illinois at Urbana-Champaign", "domain": "illinois.edu", "weight": 91},
    {"id": 3557, "name": "University of Minnesota Twin Cities", "domain": "umn.edu", "weight": 88},
    {"id": 3483, "name": "University of California, Davis", "domain": "ucdavis.edu", "weight": 89},
    {"id": 3487, "name": "University of California, Irvine", "domain": "uci.edu", "weight": 88},
    {"id": 3502, "name": "University of California, Santa Barbara", "domain": "ucsb.edu", "weight": 87},
    {"id": 2874, "name": "Santa Monica College", "domain": "smc.edu", "weight": 85},
    {"id": 2350, "name": "Northern Virginia Community College", "domain": "nvcc.edu", "weight": 84},
    
    # =========== NEGARA LAIN ===========
    {"id": 328355, "name": "University of Toronto", "domain": "utoronto.ca", "weight": 40},
    {"id": 328315, "name": "University of British Columbia", "domain": "ubc.ca", "weight": 38},
    {"id": 273409, "name": "University of Oxford", "domain": "ox.ac.uk", "weight": 35},
    {"id": 273378, "name": "University of Cambridge", "domain": "cam.ac.uk", "weight": 35},
    {"id": 10007277, "name": "Indian Institute of Technology Delhi", "domain": "iitd.ac.in", "weight": 20},
    {"id": 3819983, "name": "University of Mumbai", "domain": "mu.ac.in", "weight": 15},
    {"id": 345301, "name": "The University of Melbourne", "domain": "unimelb.edu.au", "weight": 30},
    {"id": 345303, "name": "The University of Sydney", "domain": "sydney.edu.au", "weight": 28},
]

def select_university() -> Dict:
    """Pemilihan acak berbobot berdasarkan tingkat keberhasilan"""
    weights = []
    for uni in UNIVERSITIES:
        success_rate = stats.get_rate(uni["name"])
        weight = uni["weight"] * (success_rate / 50) if success_rate > 0 else uni["weight"]
        weights.append(max(1, weight))
    
    total = sum(weights)
    if total == 0:
        return {**UNIVERSITIES[0], "idExtended": str(UNIVERSITIES[0]["id"])}
    
    r = random.uniform(0, total)
    
    cumulative = 0
    for uni, weight in zip(UNIVERSITIES, weights):
        cumulative += weight
        if r <= cumulative:
            return {**uni, "idExtended": str(uni["id"])}
    return {**UNIVERSITIES[0], "idExtended": str(UNIVERSITIES[0]["id"])}


# ============ UTILITAS ============
FIRST_NAMES = [
    "Liam", "Noah", "Oliver", "Elijah", "Lucas", "Mason", "Logan", "Alexander", "Ethan", "Jacob",
    "Michael", "Daniel", "Henry", "Jackson", "Sebastian", "Aiden", "Matthew", "Samuel", "David", "Joseph",
    "Carter", "Owen", "Wyatt", "John", "Jack", "Luke", "Jayden", "Dylan", "Grayson", "Levi",
    "Isaac", "Gabriel", "Julian", "Mateo", "Anthony", "Jaxon", "Lincoln", "Joshua", "Christopher", "Andrew",
    "Theodore", "Caleb", "Ryan", "Asher", "Nathan", "Thomas", "Leo", "Isaiah", "Charles", "Josiah",
    "James", "Robert", "William", "Richard", "Kenneth", "Kevin", "Brian", "George", "Timothy", "Ronald",
    "Edward", "Jason", "Jeffrey", "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly",
    "Emily", "Donna", "Michelle", "Dorothy", "Carol", "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca",
    "Sharon", "Laura", "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Mia", "Charlotte", "Amelia",
    "Sophia", "Emma", "Olivia", "Ava", "Isabella", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn",
    "Abigail", "Emily", "Elizabeth", "Mila", "Ella", "Avery", "Sofia", "Camila", "Aria", "Scarlett",
    "Victoria", "Madison", "Luna", "Grace", "Chloe", "Penelope", "Layla", "Riley", "Zoey", "Nora",
    "Lily", "Eleanor", "Hannah", "Lillian", "Addison", "Aubrey", "Ellie", "Stella", "Natalie", "Zoe",
    "Leah", "Hazel", "Violet", "Aurora", "Savannah", "Audrey", "Brooklyn", "Bella", "Claire", "Skylar"
]
LAST_NAMES = [
    "Miller", "Davis", "Garcia", "Rodriguez", "Wilson", "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez",
    "Moore", "Martin", "Jackson", "Thompson", "White", "Lopez", "Lee", "Gonzalez", "Harris", "Clark",
    "Lewis", "Robinson", "Walker", "Perez", "Hall", "Young", "Allen", "Sanchez", "Wright", "King",
    "Scott", "Green", "Baker", "Adams", "Nelson", "Hill", "Ramirez", "Campbell", "Mitchell", "Roberts",
    "Carter", "Phillips", "Evans", "Turner", "Torres", "Parker", "Collins", "Edwards", "Stewart", "Flores",
    "Morris", "Nguyen", "Murphy", "Rivera", "Cook", "Rogers", "Morgan", "Peterson", "Cooper", "Reed",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez",
    "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee",
    "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts", "Turner",
    "Phillips", "Evans", "Parker", "Edwards", "Collins", "Stewart", "Morris", "Murphy", "Cook", "Rogers",
    "Morgan", "Peterson", "Cooper", "Reed", "Bailey", "Bell", "Gomez", "Kelly", "Howard", "Ward",
    "Cox", "Diaz", "Richardson", "Wood", "Watson", "Brooks", "Bennett", "Gray", "James", "Reyes",
    "Cruz", "Hughes", "Price", "Myers", "Long", "Foster", "Sanders", "Ross", "Morales", "Powell",
    "Sullivan", "Russell", "Ortiz", "Jenkins", "Gutierrez", "Perry", "Butler", "Barnes", "Fisher", "Henderson",
    "Coleman", "Simmons", "Patterson", "Jordan", "Reynolds", "Hamilton", "Graham", "Kim", "Gonzales", "Alexander",
    "Ramos", "Wallace", "Griffin", "West", "Cole", "Hayes", "Chavez", "Gibson", "Bryant", "Ellis",
    "Stevens", "Murray", "Ford", "Marshall", "Owens", "Mcdonald", "Harrison", "Ruiz", "Kennedy", "Wells",
    "Alvarez", "Woods", "Mendoza", "Castillo", "Olson"
]


def random_delay():
    time.sleep(random.randint(MIN_DELAY, MAX_DELAY) / 2000)


def generate_fingerprint() -> str:
    """Menghasilkan sidik jari browser yang realistis"""
    resolutions = ["1920x1080", "1366x768", "1536x864", "1440x900", "1280x720", "2560x1440"]
    timezones = [-8, -7, -6, -5, -4, 0, 1, 2, 3, 5.5, 8, 9, 10]
    languages = ["en-US", "en-GB", "en-CA", "en-AU", "es-ES", "fr-FR", "de-DE", "pt-BR"]
    platforms = ["Win32", "MacIntel", "Linux x86_64"]
    vendors = ["Google Inc.", "Apple Computer, Inc.", ""]
    
    components = [
        str(int(time.time() * 1000)),
        str(random.random()),
        random.choice(resolutions),
        str(random.choice(timezones)),
        random.choice(languages),
        random.choice(platforms),
        random.choice(vendors),
        str(random.randint(1, 16)),
        str(random.randint(2, 32)),
        str(random.randint(0, 1)),
    ]
    return hashlib.md5("|".join(components).encode()).hexdigest()


def generate_name() -> Tuple[str, str]:
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)


def generate_email(first: str, last: str, domain: str) -> str:
    first = first.lower()
    last = last.lower()
    patterns = [
        f"{first[0]}{last}{random.randint(100, 999)}",
        f"{first}.{last}{random.randint(10, 99)}",
        f"{last}{first[0]}{random.randint(100, 999)}"
    ]
    return f"{random.choice(patterns)}@{domain}"


def generate_birth_date() -> str:
    year = random.randint(2000, 2006)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


# ============ GENERATOR DOKUMEN ============
def generate_transcript(first: str, last: str, school: str, dob: str) -> bytes:
    """Menghasilkan transkrip akademik palsu"""
    w, h = 850, 1100
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font_header = ImageFont.truetype("arial.ttf", 32)
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 16)
        try:
            font_bold = ImageFont.truetype("arialbd.ttf", 16)
        except:
            font_bold = ImageFont.truetype("arial.ttf", 16)
    except:
        font_header = font_title = font_text = font_bold = ImageFont.load_default()
    
    # Header
    draw.text((w//2, 50), school.upper(), fill=(0, 0, 0), font=font_header, anchor="mm")
    draw.text((w//2, 90), "OFFICIAL ACADEMIC TRANSCRIPT", fill=(50, 50, 50), font=font_title, anchor="mm")
    draw.line([(50, 110), (w-50, 110)], fill=(0, 0, 0), width=2)
    
    # Informasi Siswa
    y = 150
    draw.text((50, y), f"Student Name: {first} {last}", fill=(0, 0, 0), font=font_bold)
    draw.text((w-300, y), f"Student ID: {random.randint(10000000, 99999999)}", fill=(0, 0, 0), font=font_text)
    y += 30
    draw.text((50, y), f"Date of Birth: {dob}", fill=(0, 0, 0), font=font_text)
    draw.text((w-300, y), f"Date Issued: {time.strftime('%Y-%m-%d')}", fill=(0, 0, 0), font=font_text)
    y += 40
    
    # Status Pendaftaran
    draw.rectangle([(50, y), (w-50, y+40)], fill=(240, 240, 240))
    draw.text((w//2, y+20), "CURRENT STATUS: ENROLLED (SPRING 2025)", fill=(0, 100, 0), font=font_bold, anchor="mm")
    y += 70
    
    # Mata Kuliah
    courses = [
        ("CS 101", "Intro to Computer Science", "4.0", "A"),
        ("MATH 201", "Calculus I", "3.0", "A-"),
        ("ENG 102", "Academic Writing", "3.0", "B+"),
        ("PHYS 150", "Physics for Engineers", "4.0", "A"),
        ("HIST 110", "World History", "3.0", "A")
    ]
    
    # Header Tabel
    draw.text((50, y), "Course Code", font=font_bold, fill=(0,0,0))
    draw.text((200, y), "Course Title", font=font_bold, fill=(0,0,0))
    draw.text((600, y), "Credits", font=font_bold, fill=(0,0,0))
    draw.text((700, y), "Grade", font=font_bold, fill=(0,0,0))
    y += 20
    draw.line([(50, y), (w-50, y)], fill=(0, 0, 0), width=1)
    y += 20
    
    for code, title, cred, grade in courses:
        draw.text((50, y), code, font=font_text, fill=(0,0,0))
        draw.text((200, y), title, font=font_text, fill=(0,0,0))
        draw.text((600, y), cred, font=font_text, fill=(0,0,0))
        draw.text((700, y), grade, font=font_text, fill=(0,0,0))
        y += 30
    
    y += 20
    draw.line([(50, y), (w-50, y)], fill=(0, 0, 0), width=1)
    y += 30
    
    # Ringkasan
    draw.text((50, y), "Cumulative GPA: 3.85", font=font_bold, fill=(0,0,0))
    draw.text((w-300, y), "Academic Standing: Good", font=font_bold, fill=(0,0,0))
    
    # Footer
    draw.text((w//2, h-50), "This document is electronically generated and valid without signature.", 
              fill=(100, 100, 100), font=font_text, anchor="mm")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_student_id(first: str, last: str, school: str) -> bytes:
    """Menghasilkan kartu mahasiswa palsu"""
    w, h = 650, 400
    bg_color = (random.randint(240, 255), random.randint(240, 255), random.randint(240, 255))
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)
    
    try:
        font_lg = ImageFont.truetype("arial.ttf", 26)
        font_md = ImageFont.truetype("arial.ttf", 18)
        font_sm = ImageFont.truetype("arial.ttf", 14)
        try:
            font_bold = ImageFont.truetype("arialbd.ttf", 20)
        except:
            font_bold = ImageFont.truetype("arial.ttf", 20)
    except:
        font_lg = font_md = font_sm = font_bold = ImageFont.load_default()
    
    header_color = (random.randint(0, 50), random.randint(0, 50), random.randint(50, 150))
    
    draw.rectangle([(0, 0), (w, 80)], fill=header_color)
    draw.text((w//2, 40), school.upper(), fill=(255, 255, 255), font=font_lg, anchor="mm")
    
    # Foto placeholder
    draw.rectangle([(30, 100), (160, 280)], outline=(100, 100, 100), width=2, fill=(220, 220, 220))
    draw.text((95, 190), "PHOTO", fill=(150, 150, 150), font=font_md, anchor="mm")
    
    # Info
    x_info = 190
    y = 110
    draw.text((x_info, y), f"{first} {last}", fill=(0, 0, 0), font=font_bold)
    y += 40
    draw.text((x_info, y), "Student ID:", fill=(100, 100, 100), font=font_sm)
    draw.text((x_info + 80, y), str(random.randint(10000000, 99999999)), fill=(0, 0, 0), font=font_md)
    y += 30
    draw.text((x_info, y), "Role:", fill=(100, 100, 100), font=font_sm)
    draw.text((x_info + 80, y), "Student", fill=(0, 0, 0), font=font_md)
    y += 30
    draw.text((x_info, y), "Valid Thru:", fill=(100, 100, 100), font=font_sm)
    draw.text((x_info + 80, y), f"05/{int(time.strftime('%Y'))+1}", fill=(0, 0, 0), font=font_md)
    
    # Barcode strip
    draw.rectangle([(0, 320), (w, 380)], fill=(255, 255, 255))
    for i in range(40):
        x = 50 + i * 14
        if random.random() > 0.3:
            draw.rectangle([(x, 330), (x+8, 370)], fill=(0, 0, 0))
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ============ VERIFIKASI ============
class GeminiVerifier:
    """Google One (Gemini AI Pro) Verifikasi Mahasiswa"""
    
    def __init__(self, url: str, proxy: str = None):
        self.url = url
        self.vid = self._parse_id(url)
        self.fingerprint = generate_fingerprint()
        
        # Konfigurasi proxy yang benar untuk httpx
        client_args = {"timeout": 30.0}
        if proxy:
            if not proxy.startswith(("http://", "https://")):
                proxy = f"http://{proxy}"
            client_args["proxies"] = proxy
        
        self.client = httpx.Client(**client_args)
        self.org = None
    
    def __del__(self):
        if hasattr(self, "client"):
            try:
                self.client.close()
            except:
                pass
    
    @staticmethod
    def _parse_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _request(self, method: str, endpoint: str, body: Dict = None) -> Tuple[Dict, int]:
        random_delay()
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            resp = self.client.request(
                method, 
                f"{SHEERID_API_URL}{endpoint}", 
                json=body, 
                headers=headers,
                follow_redirects=True
            )
            return resp.json() if resp.text else {}, resp.status_code
        except httpx.TimeoutException:
            raise Exception("Timeout: Permintaan terlalu lama")
        except Exception as e:
            raise Exception(f"Permintaan gagal: {e}")
    
    def _upload_s3(self, url: str, data: bytes) -> bool:
        try:
            headers = {"Content-Type": "image/png"}
            resp = self.client.put(url, content=data, headers=headers, timeout=60.0)
            return 200 <= resp.status_code < 300
        except Exception as e:
            print(f"    Upload error: {e}")
            return False
    
    def check_link(self) -> Dict:
        """Periksa apakah tautan verifikasi valid"""
        if not self.vid:
            return {"valid": False, "error": "URL tidak valid"}
        
        try:
            data, status = self._request("GET", f"/verification/{self.vid}")
            if status != 200:
                return {"valid": False, "error": f"HTTP {status}"}
            
            step = data.get("currentStep", "")
            valid_steps = ["collectStudentPersonalInfo", "docUpload", "sso"]
            
            if step in valid_steps:
                return {"valid": True, "step": step}
            elif step == "success":
                return {"valid": False, "error": "Sudah diverifikasi"}
            elif step == "pending":
                return {"valid": False, "error": "Sudah menunggu review"}
            else:
                return {"valid": False, "error": f"Langkah tidak valid: {step}"}
                
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def verify(self) -> Dict:
        """Jalankan verifikasi lengkap"""
        if not self.vid:
            return {"success": False, "error": "URL verifikasi tidak valid"}
        
        try:
            # Periksa langkah saat ini
            check_data, check_status = self._request("GET", f"/verification/{self.vid}")
            current_step = check_data.get("currentStep", "") if check_status == 200 else ""
            
            # Hasilkan informasi
            first, last = generate_name()
            self.org = select_university()
            email = generate_email(first, last, self.org["domain"])
            dob = generate_birth_date()
            
            print(f"\n   Mahasiswa: {first} {last}")
            print(f"   Email: {email}")
            print(f"   Sekolah: {self.org['name']}")
            print(f"   Tanggal Lahir: {dob}")
            print(f"   ID: {self.vid[:20]}...")
            print(f"   Memulai langkah: {current_step}")
            
            # Hasilkan dokumen
            doc_type = "transcript" if random.random() < 0.7 else "id_card"
            if doc_type == "transcript":
                print("\n   Langkah 1/3: Membuat transkrip akademik...")
                doc = generate_transcript(first, last, self.org["name"], dob)
                filename = "transcript.png"
            else:
                print("\n   Langkah 1/3: Membuat ID mahasiswa...")
                doc = generate_student_id(first, last, self.org["name"])
                filename = "student_card.png"
            print(f"     Ukuran: {len(doc)/1024:.1f} KB")
            
            # Kirim info (jika diperlukan)
            if current_step == "collectStudentPersonalInfo":
                print("   Langkah 2/3: Mengirimkan informasi mahasiswa...")
                body = {
                    "firstName": first, 
                    "lastName": last, 
                    "birthDate": dob,
                    "email": email, 
                    "phoneNumber": "",
                    "organization": {
                        "id": self.org["id"], 
                        "idExtended": self.org["idExtended"], 
                        "name": self.org["name"]
                    },
                    "deviceFingerprintHash": self.fingerprint,
                    "locale": "en-US",
                    "metadata": {
                        "marketConsentValue": False,
                        "verificationId": self.vid,
                        "refererUrl": f"https://services.sheerid.com/verify/{PROGRAM_ID}/?verificationId={self.vid}",
                        "flags": '{"collect-info-step-email-first":"default","doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","font-size":"default","include-cvec-field-france-student":"not-labeled-optional"}',
                        "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount"
                    }
                }
                
                data, status = self._request("POST", 
                    f"/verification/{self.vid}/step/collectStudentPersonalInfo", 
                    body
                )
                
                if status != 200:
                    stats.record(self.org["name"], False)
                    return {"success": False, "error": f"Pengiriman gagal: HTTP {status}"}
                
                if data.get("currentStep") == "error":
                    stats.record(self.org["name"], False)
                    return {"success": False, "error": f"Kesalahan: {data.get('errorIds', [])}"}
                
                print(f"     Langkah saat ini: {data.get('currentStep')}")
                current_step = data.get("currentStep", "")
            elif current_step in ["docUpload", "sso"]:
                print("   Langkah 2/3: Dilewati (sudah melewati pengiriman informasi)...")
            else:
                print(f"   Langkah 2/3: Langkah tidak dikenal '{current_step}', mencoba melanjutkan...")
            
            # Lewati SSO jika diperlukan
            if current_step in ["sso", "collectStudentPersonalInfo"]:
                print("   Langkah 3/4: Melewati SSO...")
                try:
                    self._request("DELETE", f"/verification/{self.vid}/step/sso")
                except:
                    pass
            
            # Unggah dokumen
            print("   Langkah 4/5: Mengunggah dokumen...")
            upload_body = {
                "files": [{
                    "fileName": filename, 
                    "mimeType": "image/png", 
                    "fileSize": len(doc)
                }]
            }
            data, status = self._request(
                "POST", 
                f"/verification/{self.vid}/step/docUpload", 
                upload_body
            )
            
            if not data.get("documents") or len(data["documents"]) == 0:
                stats.record(self.org["name"], False)
                return {"success": False, "error": "Tidak ada URL unggah yang diterima"}
            
            upload_url = data["documents"][0].get("uploadUrl")
            if not upload_url:
                stats.record(self.org["name"], False)
                return {"success": False, "error": "URL unggah tidak ditemukan"}
            
            if not self._upload_s3(upload_url, doc):
                stats.record(self.org["name"], False)
                return {"success": False, "error": "Unggah ke S3 gagal"}
            
            print("     Dokumen berhasil diunggah!")
            
            # Selesaikan unggah
            print("   Langkah 5/5: Menyelesaikan unggah...")
            try:
                data, status = self._request("POST", f"/verification/{self.vid}/step/completeDocUpload")
                print(f"     Unggah selesai: {data.get('currentStep', 'pending')}")
            except:
                pass
            
            stats.record(self.org["name"], True)
            
            return {
                "success": True,
                "message": "Verifikasi diajukan! Tunggu 24-48 jam untuk review.",
                "student": f"{first} {last}",
                "email": email,
                "school": self.org["name"],
                "redirectUrl": data.get("redirectUrl") if 'data' in locals() else None
            }
            
        except Exception as e:
            if self.org:
                stats.record(self.org["name"], False)
            return {"success": False, "error": str(e)}


# ============ UTAMA ============
def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Google One (Gemini AI Pro) Alat Verifikasi Mahasiswa",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("url", nargs="?", help="URL verifikasi")
    parser.add_argument("--proxy", help="Server proxy (host:port atau http://user:pass@host:port)")
    args = parser.parse_args()
    
    print()
    print("=" * 60)
    print(" Alat Verifikasi Google One (Gemini AI Pro) ".center(60))
    print(" Diskon Mahasiswa SheerID ".center(60))
    print("=" * 60)
    print()
    
    # Dapatkan URL
    if args.url:
        url = args.url
    else:
        url = input("   Masukkan URL verifikasi: ").strip()
    
    if not url or "sheerid.com" not in url:
        print("\n   URL tidak valid. Harus mengandung sheerid.com")
        sys.exit(1)
    
    # Tampilkan info proxy
    if args.proxy:
        print(f"   Menggunakan proxy: {args.proxy}")
    
    print("\n   Memproses...")
    
    try:
        verifier = GeminiVerifier(url, proxy=args.proxy)
        
        # Periksa tautan terlebih dahulu
        check = verifier.check_link()
        if not check.get("valid"):
            print(f"\n   Kesalahan Tautan: {check.get('error')}")
            sys.exit(1)
        
        result = verifier.verify()
        
        print()
        print("-" * 58)
        if result.get("success"):
            print("   BERHASIL!")
            print(f"   Mahasiswa: {result.get('student')}")
            print(f"   Email: {result.get('email')}")
            print(f"   Sekolah: {result.get('school')}")
            print()
            print("   Tunggu 24-48 jam untuk review manual")
        else:
            print(f"   GAGAL: {result.get('error')}")
        print("-" * 58)
        
        stats.print_stats()
        
    except KeyboardInterrupt:
        print("\n\n   Dibatalkan oleh pengguna.")
        sys.exit(0)
    except Exception as e:
        print(f"\n   Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()