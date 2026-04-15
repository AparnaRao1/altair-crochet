import os
import uuid
import torch

from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATED_DIR = os.path.join(BASE_DIR, "generated")

os.makedirs(GENERATED_DIR, exist_ok=True)



DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32



pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=DTYPE
)

pipe.scheduler = DPMSolverMultistepScheduler.from_config(
    pipe.scheduler.config
)

pipe = pipe.to(DEVICE)

pipe.safety_checker = None

if DEVICE == "cuda":
    pipe.enable_attention_slicing()
    pipe.enable_xformers_memory_efficient_attention()




def build_prompt(user_prompt):
    """
    Converts user request into stronger SD prompt.
    """

    return f"""
    handmade crochet product, amigurumi style, yarn texture,
    soft detailed stitches, cute aesthetic, premium handcrafted,
    product photography, clean background,
    {user_prompt}
    """


def generate_image(user_prompt):
    """
    Generates image from prompt.
    Returns filename only.
    """

    prompt = build_prompt(user_prompt)

    negative_prompt = """
    blurry, bad anatomy, ugly, deformed,
    extra limbs, duplicate, low quality,
    watermark, text, cropped, worst quality
    """

    try:
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=28,
            guidance_scale=8,
            height=512,
            width=512
        ).images[0]

        filename = f"{uuid.uuid4().hex}.png"

        save_path = os.path.join(GENERATED_DIR, filename)

        image.save(save_path)

        return filename

    except Exception as e:
        print("Image generation error:", e)
        return None


if __name__ == "__main__":

    file = generate_image(
        "Tanjiro crochet plushie, green black outfit, 25 cm"
    )

    print("Saved:", file)