"""
Engineering Unit Conversions for PyAct

A collection of helper functions to seamlessly convert values between 
Metric (SI) and Imperial / US Customary systems.
"""

# ==========================================
# LENGTH CONVERSIONS
# ==========================================

def mm_to_inch(mm: float) -> float:
    """Converts millimeters [mm] to inches [in]"""
    return mm / 25.4

def inch_to_mm(inch: float) -> float:
    """Converts inches [in] to millimeters [mm]"""
    return inch * 25.4

def m_to_ft(m: float) -> float:
    """Converts meters [m] to feet [ft]"""
    return m * 3.280839895

def ft_to_m(ft: float) -> float:
    """Converts feet [ft] to meters [m]"""
    return ft / 3.280839895

# ==========================================
# AREA & VOLUME CONVERSIONS
# ==========================================

def mm2_to_in2(mm2: float) -> float:
    """Converts square millimeters [mm^2] to square inches [in^2]"""
    return mm2 / 645.16

def in2_to_mm2(in2: float) -> float:
    """Converts square inches [in^2] to square millimeters [mm^2]"""
    return in2 * 645.16

def m3_to_ft3(m3: float) -> float:
    """Converts cubic meters [m^3] to cubic feet [ft^3]"""
    return m3 * 35.3146667

def ft3_to_m3(ft3: float) -> float:
    """Converts cubic feet [ft^3] to cubic meters [m^3]"""
    return ft3 / 35.3146667

# ==========================================
# MASS & FORCE CONVERSIONS
# ==========================================

def kg_to_lbs(kg: float) -> float:
    """Converts kilograms [kg] to pounds-mass [lbs]"""
    return kg * 2.20462262

def lbs_to_kg(lbs: float) -> float:
    """Converts pounds-mass [lbs] to kilograms [kg]"""
    return lbs / 2.20462262

def kn_to_kips(kn: float) -> float:
    """Converts kilonewtons [kN] to kilopounds-force [kips]"""
    return kn * 0.224808943

def kips_to_kn(kips: float) -> float:
    """Converts kilopounds-force [kips] to kilonewtons [kN]"""
    return kips / 0.224808943

def n_to_lbf(n: float) -> float:
    """Converts newtons [N] to pounds-force [lbf]"""
    return n * 0.224808943

def lbf_to_n(lbf: float) -> float:
    """Converts pounds-force [lbf] to newtons [N]"""
    return lbf / 0.224808943

# ==========================================
# PRESSURE & STRESS CONVERSIONS
# ==========================================

def mpa_to_psi(mpa: float) -> float:
    """Converts Megapascals [MPa] (or N/mm^2) to pounds per square inch [psi]"""
    return mpa * 145.037738

def psi_to_mpa(psi: float) -> float:
    """Converts pounds per square inch [psi] to Megapascals [MPa]"""
    return psi / 145.037738

def mpa_to_ksi(mpa: float) -> float:
    """Converts Megapascals [MPa] to kilopounds per square inch [ksi]"""
    return mpa * 0.145037738

def ksi_to_mpa(ksi: float) -> float:
    """Converts kilopounds per square inch [ksi] to Megapascals [MPa]"""
    return ksi / 0.145037738

# ==========================================
# MOMENT & TORQUE CONVERSIONS
# ==========================================

def knm_to_kipft(knm: float) -> float:
    """Converts kilonewton-meters [kNm] to kilopound-feet [kip-ft]"""
    return knm * 0.737562149

def kipft_to_knm(kipft: float) -> float:
    """Converts kilopound-feet [kip-ft] to kilonewton-meters [kNm]"""
    return kipft / 0.737562149

def knm_to_lbfft(knm: float) -> float:
    """Converts kilonewton-meters [kNm] to pound-force feet [lbf-ft]"""
    return knm * 737.562149

def lbfft_to_knm(lbfft: float) -> float:
    """Converts pound-force feet [lbf-ft] to kilonewton-meters [kNm]"""
    return lbfft / 737.562149

# ==========================================
# TEMPERATURE CONVERSIONS
# ==========================================

def c_to_f(celsius: float) -> float:
    """Converts degrees Celsius [°C] to degrees Fahrenheit [°F]"""
    return (celsius * 9/5) + 32

def f_to_c(fahrenheit: float) -> float:
    """Converts degrees Fahrenheit [°F] to degrees Celsius [°C]"""
    return (fahrenheit - 32) * 5/9
