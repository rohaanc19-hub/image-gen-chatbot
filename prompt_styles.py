STYLE_SUFFIXES = {
    "Realistic": "photorealistic, high detail, natural lighting, 8k",
    "Anime": "anime style, detailed, vibrant colors, studio anime art",
    "Cyberpunk": "cyberpunk aesthetic, neon lights, futuristic, high contrast, rain-slicked streets",
    "Watercolor": "watercolor painting, soft brush strokes, pastel tones, paper texture",
    "3D Render": "3d render, octane render, studio lighting, smooth shading, high detail",
    "Sketch": "pencil sketch, black and white, hand-drawn line art, crosshatching",
}

DEFAULT_NEGATIVE_PROMPT = "blurry, low quality, distorted, watermark, text, extra limbs"


def list_styles():
    return list(STYLE_SUFFIXES.keys())


def build_final_prompt(user_prompt, style):
    user_prompt = user_prompt.strip().rstrip(",")
    suffix = STYLE_SUFFIXES.get(style, "")
    if not suffix:
        return user_prompt
    return user_prompt + ", " + suffix
