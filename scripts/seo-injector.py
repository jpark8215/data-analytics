import os
import re
from datetime import datetime

BASE_URL = "https://jpark8215.github.io/data-analytics"
AUTHOR_NAME = "Jieun Park"
AUTHOR_TITLE = "AI Engineer & Director of Business Intelligence"
AUTHOR_URL = "https://www.linkedin.com/in/developerjp/"

BLOG_DIR = os.path.join(os.path.dirname(__file__), "..", "blogs")
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

def extract_metadata(html_content):
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    title = title_match.group(1).split('|')[0].strip() if title_match else "Blog Post"
    
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html_content, re.IGNORECASE | re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""
    
    img_match = re.search(r'<img[^>]+src=["\'](.*?)["\'][^>]+class=["\']post-image["\']', html_content, re.IGNORECASE)
    image = img_match.group(1).replace('../', '/') if img_match else "/assets/images/default.png"
    
    return title, description, image

def get_author_bio():
    return f"""
            <!-- Author Bio Section -->
            <div style="margin-top: 4rem; padding: 2rem; background: rgba(59,130,246,0.05); border-radius: var(--radius-l); border-left: 4px solid var(--clr-primary);">
                <h3 style="margin-top: 0; font-size: 1.5rem; color: var(--clr-text-main);">About the Author</h3>
                <p style="font-size: 1.1rem; color: var(--clr-text-muted); line-height: 1.6; margin-bottom: 1rem;">
                    <strong>{AUTHOR_NAME}</strong> is an {AUTHOR_TITLE}. With extensive experience in transforming raw data into actionable strategic insights, Jieun Park writes about the intersection of data architecture, analytics, and business impact.
                </p>
                <a href="{AUTHOR_URL}" target="_blank" style="display: inline-block; padding: 0.5rem 1.2rem; background: var(--clr-primary); color: white; text-decoration: none; border-radius: var(--radius-m); font-weight: 500;">Connect on LinkedIn</a>
            </div>
"""

def generate_json_ld(title, description, image_url, post_url):
    return f"""
    <!-- SEO & JSON-LD Schema injected by script -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{BASE_URL}{image_url}">
    <meta property="og:url" content="{post_url}">
    <meta property="og:type" content="article">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="canonical" href="{post_url}">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "{title}",
      "description": "{description}",
      "image": "{BASE_URL}{image_url}",
      "author": {{
        "@type": "Person",
        "name": "{AUTHOR_NAME}",
        "jobTitle": "{AUTHOR_TITLE}",
        "url": "{AUTHOR_URL}"
      }}
    }}
    </script>"""

def process_file(filepath, url_path):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already processed
    if "SEO & JSON-LD Schema injected by script" in content:
        print(f"Skipping {os.path.basename(filepath)} - already processed.")
        return True
        
    title, description, image = extract_metadata(content)
    post_url = f"{BASE_URL}/{url_path}"
    
    head_injection = generate_json_ld(title, description, image, post_url)
    bio_injection = get_author_bio()
    
    # Inject into head
    content = re.sub(r'</head>', f'{head_injection}\n</head>', content, flags=re.IGNORECASE)
    
    # Inject bio before </article>
    content = re.sub(r'</article>', f'{bio_injection}\n        </article>', content, flags=re.IGNORECASE)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Processed {os.path.basename(filepath)}")
    return True

def generate_sitemap_and_robots(urls):
    # sitemap.xml
    sitemap_path = os.path.join(ROOT_DIR, 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url in urls:
            f.write('  <url>\n')
            f.write(f'    <loc>{url}</loc>\n')
            f.write(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n')
            f.write('  </url>\n')
        f.write('</urlset>')
    print("Generated sitemap.xml")

    # robots.txt
    robots_path = os.path.join(ROOT_DIR, 'robots.txt')
    with open(robots_path, 'w', encoding='utf-8') as f:
        f.write("User-agent: *\n")
        f.write("Allow: /\n\n")
        f.write(f"Sitemap: {BASE_URL}/sitemap.xml\n")
    print("Generated robots.txt")

def main():
    urls = []
    
    # Process home pages
    urls.append(f"{BASE_URL}/index.html")
    urls.append(f"{BASE_URL}/all-posts.html")
    
    # Process blog posts
    for filename in os.listdir(BLOG_DIR):
        if filename.endswith(".html"):
            filepath = os.path.join(BLOG_DIR, filename)
            url_path = f"blogs/{filename}"
            process_file(filepath, url_path)
            urls.append(f"{BASE_URL}/{url_path}")
            
    generate_sitemap_and_robots(urls)
    print("Optimization complete!")

if __name__ == "__main__":
    main()
