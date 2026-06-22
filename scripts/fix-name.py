import os

BLOG_DIR = os.path.join(os.path.dirname(__file__), "..", "blogs")

def fix_name(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    # Replace in JSON-LD and Bio
    content = content.replace("J. Park", "Jieun Park")
    content = content.replace("AI Engineer & Director of business intelligence", "AI Engineer and Director of Business Intelligence")

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated identity in {os.path.basename(filepath)}")

def main():
    for filename in os.listdir(BLOG_DIR):
        if filename.endswith(".html"):
            filepath = os.path.join(BLOG_DIR, filename)
            fix_name(filepath)
            
    print("Identity update complete!")

if __name__ == "__main__":
    main()
