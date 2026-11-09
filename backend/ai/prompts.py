"""Catalog of presets (single source of truth for UI + prompts) and prompt templates."""

CATEGORIES = {
    "necklace": {"label": "Necklace", "noun": "necklace", "placement": "around the model's neck, resting naturally on the collarbone"},
    "earrings": {"label": "Earrings", "noun": "pair of earrings", "placement": "on both of the model's earlobes, hair tucked back so they are fully visible"},
    "ring": {"label": "Ring", "noun": "ring", "placement": "on the model's ring finger, hand elegantly posed near the face or chest"},
    "bangles": {"label": "Bangles", "noun": "set of bangles", "placement": "stacked on the model's wrist, forearm gracefully raised"},
    "bracelet": {"label": "Bracelet", "noun": "bracelet", "placement": "on the model's wrist, hand relaxed and visible"},
    "pendant": {"label": "Pendant", "noun": "pendant", "placement": "on a chain around the model's neck, centred on the chest"},
    "jewellery_set": {"label": "Jewellery Set", "noun": "jewellery set", "placement": "with every piece worn in its natural position (necklace on neck, earrings on ears)"},
    "other": {"label": "Other", "noun": "jewellery piece", "placement": "in its natural wearing position"},
}

STYLES = {
    "luxury_black": {"label": "Luxury Black", "swatch": ["#0d0c0b", "#2a2522"], "prompt": "high-end luxury product shot on a deep matte black background with a subtle gradient falloff and crisp specular highlights"},
    "premium_white": {"label": "Premium White", "swatch": ["#ffffff", "#ecebe8"], "prompt": "clean premium e-commerce shot on a seamless pure white background with a soft contact shadow"},
    "beige_studio": {"label": "Beige Studio", "swatch": ["#e9dcc7", "#cdb999"], "prompt": "warm beige studio set with a smooth paper backdrop and gentle tonal gradient"},
    "marble": {"label": "Marble Surface", "swatch": ["#f2f0ec", "#c9c4bb"], "prompt": "polished white Carrara marble surface with soft grey veining, shallow depth of field"},
    "velvet": {"label": "Velvet", "swatch": ["#3b0f1b", "#6d1f33"], "prompt": "rich velvet display surface in deep jewel tones, soft fabric texture and luxurious sheen"},
    "silk": {"label": "Silk Drape", "swatch": ["#efe2cf", "#d8b98a"], "prompt": "flowing champagne silk fabric draped in soft folds, elegant reflections"},
    "minimal_catalogue": {"label": "Minimal Catalogue", "swatch": ["#f6f4f0", "#dedad3"], "prompt": "minimalist catalogue photograph, neutral light-grey backdrop, even lighting, centred composition"},
    "royal_indian": {"label": "Royal Indian", "swatch": ["#6b1d1d", "#c89b3c"], "prompt": "regal Indian setting with carved brass, maroon brocade textile and marigold accents, heritage palace mood"},
    "bridal": {"label": "Bridal", "swatch": ["#f4d9d0", "#b9485a"], "prompt": "romantic Indian bridal flat-lay with red-gold bridal fabric, rose petals and soft bokeh"},
    "editorial": {"label": "Editorial", "swatch": ["#26221f", "#9c8b74"], "prompt": "fashion-magazine editorial still life with bold directional light, sculptural props and artistic shadows"},
    "macro": {"label": "Macro Detail", "swatch": ["#1b1a19", "#7b6a52"], "prompt": "extreme macro close-up revealing stone facets, metal texture and craftsmanship, very shallow depth of field"},
}

LIGHTING = {
    "soft_diffused": {"label": "Soft diffused", "prompt": "soft diffused studio lighting with large softboxes"},
    "dramatic_spot": {"label": "Dramatic spotlight", "prompt": "dramatic single spotlight with deep shadows and sparkling highlights"},
    "golden_warm": {"label": "Warm golden", "prompt": "warm golden-hour toned light enhancing gold metal"},
    "bright_catalogue": {"label": "Bright catalogue", "prompt": "bright, even, shadow-minimised catalogue lighting"},
    "rim_light": {"label": "Rim light", "prompt": "rim lighting outlining the silhouette with a dark surround"},
}

ANGLES = {
    "front": {"label": "Front view", "prompt": "straight-on front view at eye level"},
    "top_down": {"label": "Top-down flat lay", "prompt": "top-down flat-lay perspective"},
    "three_quarter": {"label": "45° angle", "prompt": "three-quarter 45-degree hero angle"},
    "side": {"label": "Side profile", "prompt": "side profile view showing depth"},
    "close_up": {"label": "Close-up", "prompt": "tight close-up framing filling most of the frame"},
}

BACKGROUNDS = {
    "auto": {"label": "Match style", "prompt": ""},
    "ivory": {"label": "Warm ivory", "prompt": "warm ivory"},
    "black": {"label": "Deep black", "prompt": "deep black"},
    "white": {"label": "Pure white", "prompt": "pure white"},
    "champagne": {"label": "Champagne gold", "prompt": "soft champagne gold"},
    "emerald": {"label": "Emerald green", "prompt": "deep emerald green"},
    "maroon": {"label": "Royal maroon", "prompt": "royal maroon"},
    "blush": {"label": "Blush pink", "prompt": "muted blush pink"},
}

ASPECT_RATIOS = {"1:1": (1, 1), "4:5": (4, 5), "3:4": (3, 4), "9:16": (9, 16), "16:9": (16, 9)}
DIMENSIONS = {"1024": {"label": "Standard · 1024px"}, "1536": {"label": "High · 1536px"}, "2048": {"label": "Large · 2048px"}}
ACCURACY = {
    "exact": {"label": "Pixel-exact", "description": "Your real jewellery pixels, untouched. AI builds the studio set, light and shadow around them."},
    "reshoot": {"label": "AI studio re-shoot", "description": "AI re-lights the piece for a full studio look. Tiny details can shift, so each image is inspected and retried."},
}

MODEL_PRESETS = {
    "traditional_bridal": {"label": "Traditional Indian Bridal", "defaults": {"clothing": "lehenga", "background": "palace"}, "prompt": "traditional Indian bridal look with bridal makeup, sindoor and mehendi, richly embroidered red attire"},
    "south_indian": {"label": "South Indian Traditional", "defaults": {"clothing": "kanjeevaram", "background": "temple"}, "prompt": "South Indian traditional look with jasmine flowers in braided hair and a Kanjeevaram silk saree"},
    "north_indian_bridal": {"label": "North Indian Bridal", "defaults": {"clothing": "lehenga", "background": "palace"}, "prompt": "North Indian bridal look with a heavily embroidered lehenga and dupatta draped over the head"},
    "modern_fashion": {"label": "Modern Fashion", "defaults": {"clothing": "black_top", "background": "studio_ivory"}, "prompt": "modern contemporary fashion look, minimal makeup, chic styling"},
    "festive": {"label": "Festive", "defaults": {"clothing": "anarkali", "background": "festive_lights"}, "prompt": "festive celebration look with vibrant colours and a joyful expression, warm diya light ambience"},
    "luxury_editorial": {"label": "Luxury Editorial", "defaults": {"clothing": "evening_gown", "background": "dark_studio"}, "prompt": "high-fashion luxury magazine editorial look with sculpted lighting and poised expression"},
}
GENDERS = {"female": {"label": "Female"}, "male": {"label": "Male"}}
APPEARANCES = {
    "fair": {"label": "Fair skin"}, "wheatish": {"label": "Wheatish skin"},
    "dusky": {"label": "Dusky skin"}, "deep": {"label": "Deep brown skin"},
}
POSES = {
    "front_portrait": {"label": "Front portrait", "prompt": "facing the camera in a head-and-shoulders portrait"},
    "three_quarter": {"label": "Three-quarter turn", "prompt": "turned three-quarters with chin slightly lifted"},
    "side_profile": {"label": "Side profile", "prompt": "in elegant side profile (ideal for earrings)"},
    "hand_closeup": {"label": "Hand close-up", "prompt": "close-up of hands and wrists gracefully posed (ideal for rings and bangles)"},
    "neckline": {"label": "Neckline close-up", "prompt": "cropped close-up of neck and collarbone (ideal for necklaces)"},
    "half_body": {"label": "Half body", "prompt": "half-body framing with a relaxed, confident posture"},
}
CLOTHING = {
    "silk_saree": {"label": "Silk saree", "prompt": "a silk saree"},
    "kanjeevaram": {"label": "Kanjeevaram saree", "prompt": "a gold-bordered Kanjeevaram silk saree"},
    "lehenga": {"label": "Bridal lehenga", "prompt": "a heavily embroidered bridal lehenga"},
    "anarkali": {"label": "Anarkali suit", "prompt": "an elegant anarkali suit"},
    "evening_gown": {"label": "Evening gown", "prompt": "an off-shoulder evening gown"},
    "black_top": {"label": "Plain black top", "prompt": "a plain black high-neck top"},
    "sherwani": {"label": "Sherwani", "prompt": "an ivory embroidered sherwani"},
    "kurta": {"label": "Kurta", "prompt": "a tailored silk kurta"},
}
MODEL_BACKGROUNDS = {
    "studio_ivory": {"label": "Ivory studio", "prompt": "a seamless warm ivory studio backdrop"},
    "palace": {"label": "Palace interior", "prompt": "an ornate Rajasthani palace interior, softly blurred"},
    "temple": {"label": "Temple courtyard", "prompt": "a South Indian temple courtyard with stone pillars, softly blurred"},
    "garden": {"label": "Garden bokeh", "prompt": "a lush garden with creamy bokeh"},
    "dark_studio": {"label": "Dark luxury studio", "prompt": "a dark luxury studio with a single warm key light"},
    "festive_lights": {"label": "Festive lights", "prompt": "warm festive diya and fairy lights bokeh"},
}

PRESERVATION_RULES = (
    "STRICT JEWELLERY PRESERVATION: The jewellery in the reference photo is a real product that must be reproduced exactly. "
    "Keep the identical design, silhouette, proportions and relative size; the exact number, shape, cut, colour and arrangement of every stone; "
    "the same metal colour and finish (yellow/rose/white gold, silver, oxidised); identical engravings, filigree, meenakari, chain and link pattern, "
    "clasps, drops and motifs. Do NOT add, remove, simplify, recolour or restyle any element. Do NOT invent additional jewellery."
)


def catalog() -> dict:
    def opts(d):
        return [{"id": k, **{x: y for x, y in v.items() if x != "prompt"}} for k, v in d.items()]
    return {
        "categories": opts(CATEGORIES), "styles": opts(STYLES), "lighting": opts(LIGHTING), "angles": opts(ANGLES),
        "backgrounds": opts(BACKGROUNDS), "aspect_ratios": [{"id": k, "label": k} for k in ASPECT_RATIOS],
        "dimensions": opts(DIMENSIONS), "model_presets": opts(MODEL_PRESETS), "genders": opts(GENDERS),
        "appearances": opts(APPEARANCES), "poses": opts(POSES), "clothing": opts(CLOTHING),
        "model_backgrounds": opts(MODEL_BACKGROUNDS), "accuracy": opts(ACCURACY),
    }


_PRODUCT_FIELDS = {"accuracy": (ACCURACY, "exact"), "lighting": (LIGHTING, "soft_diffused"), "angle": (ANGLES, "three_quarter"),
                   "background": (BACKGROUNDS, "auto"), "aspect_ratio": (ASPECT_RATIOS, "1:1"), "dimensions": (DIMENSIONS, "1536")}
_MODEL_FIELDS = {"preset": (MODEL_PRESETS, "traditional_bridal"), "gender": (GENDERS, "female"), "appearance": (APPEARANCES, "wheatish"),
                 "pose": (POSES, "front_portrait"), "clothing": (CLOTHING, "silk_saree"), "background": (MODEL_BACKGROUNDS, "studio_ivory"),
                 "aspect_ratio": (ASPECT_RATIOS, "4:5"), "dimensions": (DIMENSIONS, "1536")}


def validate_request(mode: str, category: str, style: str | None, settings: dict) -> tuple[str | None, dict]:
    """Return (style, cleaned settings) or raise ValueError for unknown options."""
    if category not in CATEGORIES:
        raise ValueError(f"Unknown jewellery category '{category}'")
    if mode == "bg_removal":
        return None, {}
    if style is not None and style not in STYLES:
        raise ValueError(f"Unknown photography style '{style}'")
    if mode == "product" and style is None:
        raise ValueError("Choose a photography style")
    fields = _PRODUCT_FIELDS if mode == "product" else _MODEL_FIELDS
    clean = {}
    for key, (options, default) in fields.items():
        value = settings.get(key) or default
        if value not in options:
            raise ValueError(f"Invalid {key} '{value}'")
        clean[key] = value
    clean["instructions"] = str(settings.get("instructions") or "").strip()[:500]
    return style, clean


def _composition(aspect: str) -> str:
    return (f"Compose for a {aspect} aspect ratio. Keep the entire jewellery visible and uncropped, sharply focused, "
            "with realistic metal reflections, natural stone sparkle and a soft believable shadow. Photorealistic commercial quality. "
            "No text, no logos, no watermarks, no hands or props covering the jewellery.")


def _variation(index: int, total: int) -> str:
    return f" This is variation {index + 1} of {total}: vary the composition or prop arrangement subtly, never the jewellery." if total > 1 else ""


DETAIL_REF = ("IMAGE 2 is a close-up crop of the same piece: use it to reproduce every stone, prong, bead, engraving and link exactly. ")


def mask_prompt(category: str) -> str:
    return (f"Create a precise segmentation matte of the {CATEGORIES[category]['noun']} in this image. Paint every pixel that belongs to the jewellery "
            "(metal, stones, chain links, drops, beads, tassels, including thin chains and tiny gaps) pure white, and every other pixel pure black "
            "(surfaces, hands, stands, boxes, tags, shadows, reflections, and the flat grey padding). Keep the exact same framing, scale and position. "
            "Do not move, crop, resize or redraw anything. Output only the black-and-white matte.")


def plate_prompt(category: str, style: str, s: dict, index: int = 0, total: int = 1) -> str:
    bg = BACKGROUNDS[s["background"]]["prompt"]
    parts = [
        f"Photorealistic, high-end empty jewellery product photography set for a {CATEGORIES[category]['noun']}: {STYLES[style]['prompt']}.",
        f"Background colour: {bg}." if bg else "",
        f"Lighting: {LIGHTING[s['lighting']]['prompt']}. Camera: {ANGLES[s['angle']]['prompt']}.",
        f"{s['aspect_ratio']} aspect ratio. The centre of the set is completely EMPTY and clear, ready for a jewellery piece to be placed. "
        "No jewellery, no people, no hands, no text, no logos, no visible studio equipment, softboxes or lamps. Commercial catalogue quality, sharp and clean.",
        f"Client notes: {s['instructions']}" if s["instructions"] else "",
    ]
    return " ".join(p for p in parts if p) + (f" Variation {index + 1} of {total}: vary props and composition subtly." if total > 1 else "")


def product_prompt(category: str, style: str, s: dict, index: int = 0, total: int = 1) -> str:
    cat, sty = CATEGORIES[category], STYLES[style]
    bg = BACKGROUNDS[s["background"]]["prompt"]
    parts = [
        "You are a world-class jewellery photographer and retoucher. Use the jewellery in the attached photo (IMAGE 1) as the exact product.",
        DETAIL_REF,
        PRESERVATION_RULES,
        f"TASK: Re-photograph this {cat['noun']} as a {sty['prompt']}.",
        f"Lighting: {LIGHTING[s['lighting']]['prompt']}. Camera: {ANGLES[s['angle']]['prompt']}.",
        f"Background colour: {bg}." if bg else "",
        _composition(s["aspect_ratio"]),
        f"Client notes (apply only if they do not alter the jewellery): {s['instructions']}" if s["instructions"] else "",
    ]
    return " ".join(p for p in parts if p) + _variation(index, total)


def model_prompt(category: str, style: str | None, s: dict, index: int = 0, total: int = 1) -> str:
    cat = CATEGORIES[category]
    parts = [
        "You are a world-class jewellery campaign photographer. Create a photorealistic photograph of a "
        f"{s['gender']} Indian model with {APPEARANCES[s['appearance']]['label'].lower()}, {MODEL_PRESETS[s['preset']]['prompt']}, wearing {CLOTHING[s['clothing']]['prompt']}, "
        f"{POSES[s['pose']]['prompt']}, against {MODEL_BACKGROUNDS[s['background']]['prompt']}.",
        f"The model wears THE EXACT {cat['noun']} from the attached photo (IMAGE 1) {cat['placement']}, at a physically realistic scale.",
        DETAIL_REF,
        PRESERVATION_RULES,
        f"Overall photographic mood: {STYLES[style]['prompt']}." if style else "",
        "Natural skin texture, anatomically correct hands and ears, the jewellery is the hero and in sharp focus.",
        _composition(s["aspect_ratio"]),
        f"Client notes (apply only if they do not alter the jewellery): {s['instructions']}" if s["instructions"] else "",
    ]
    return " ".join(p for p in parts if p) + _variation(index, total)


def background_removal_prompt(category: str, key_colour: str) -> str:
    colour = {"green": "pure chroma green (#00FF00)", "magenta": "pure magenta (#FF00FF)"}[key_colour]
    return (
        f"Isolate the {CATEGORIES[category]['noun']} from this photo. Reproduce the exact same jewellery at the same angle, scale and position. "
        f"{PRESERVATION_RULES} Replace everything that is not jewellery (surface, hands, display stands, packaging, shadows) with a perfectly flat, "
        f"uniform {colour} background. No shadows, no gradients, no colour spill on the jewellery, no other objects."
    )
