from PIL import Image
import os

def convert_png_to_ico(png_path, ico_path):
    if not os.path.exists(png_path):
        print(f"Error: {png_path} not found.")
        return
    
    img = Image.open(png_path)
    # Windows icons usually contain multiple sizes
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (255, 255)]
    img.save(ico_path, sizes=icon_sizes)
    print(f"Successfully created {ico_path}")

if __name__ == "__main__":
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    png_path = os.path.join(assets_dir, "app_icon.png")
    ico_path = os.path.join(assets_dir, "app_icon.ico")
    
    convert_png_to_ico(png_path, ico_path)
