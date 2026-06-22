import os
import re

BLOG_DIR = os.path.join(os.path.dirname(__file__), "..", "blogs")
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

NEW_BIO = """            <!-- Author Bio Section -->
            <div style="margin-top: 2rem; padding: 1rem; background: rgba(59,130,246,0.05); border-radius: var(--radius-m); border-left: 3px solid var(--clr-primary); display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap;">
                <div>
                    <h3 style="margin: 0 0 0.25rem 0; font-size: 1rem; color: var(--clr-text-main);">About the Author</h3>
                    <p style="font-size: 0.85rem; color: var(--clr-text-muted); line-height: 1.4; margin: 0;">
                        <strong>J. Park</strong> is an AI Engineer & Director of business intelligence.
                    </p>
                </div>
                <a href="https://www.linkedin.com/in/developerjp/" target="_blank" style="font-size: 0.85rem; padding: 0.4rem 0.8rem; background: var(--clr-primary); color: white; text-decoration: none; border-radius: 4px; font-weight: 500; white-space: nowrap;">Connect on LinkedIn</a>
            </div>"""

def update_bio(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find the old bio block
    pattern = r'<!-- Author Bio Section -->.*?</div>\s*'
    
    if re.search(pattern, content, flags=re.DOTALL):
        new_content = re.sub(pattern, NEW_BIO + '\n\n', content, flags=re.DOTALL)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {os.path.basename(filepath)}")
    else:
        print(f"No bio found in {os.path.basename(filepath)}")

def main():
    # Process blog posts
    for filename in os.listdir(BLOG_DIR):
        if filename.endswith(".html"):
            filepath = os.path.join(BLOG_DIR, filename)
            update_bio(filepath)
            
    print("Bio update complete!")

if __name__ == "__main__":
    main()
