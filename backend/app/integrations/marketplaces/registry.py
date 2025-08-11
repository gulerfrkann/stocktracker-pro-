from typing import Dict, Type

from .trendyol import TrendyolAdapter
from .hepsiburada import HepsiburadaAdapter
from .n11 import N11Adapter
from .pazarama import PazaramaAdapter
from .epttavm import EpttAvmAdapter
from .ciceksepeti import CicekSepetiAdapter
from .idefix import IdefixAdapter


ADAPTERS: Dict[str, object] = {
    "trendyol": TrendyolAdapter(),
    "hepsiburada": HepsiburadaAdapter(),
    "n11": N11Adapter(),
    "pazarama": PazaramaAdapter(),
    "epttavm": EpttAvmAdapter(),
    "ciceksepeti": CicekSepetiAdapter(),
    "idefix": IdefixAdapter(),
}


def get_adapter(platform: str):
    key = (platform or "").lower()
    if key not in ADAPTERS:
        raise ValueError(f"Unsupported marketplace platform: {platform}")
    return ADAPTERS[key]



