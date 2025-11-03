
import os
import markdown
import yaml
import shutil
import argparse
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

def copy_media(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

def copy_stylesheet(src, dst):
    shutil.copy(src, dst)

def main():
    # Configuration
    parser = argparse.ArgumentParser(description='Build the blog.')
    parser.add_argument('--output-dir', default='../public', help='Output directory for the generated blog.')
    args = parser.parse_args()

    SCRIPT_DIR = os.path.dirname(__file__)
    POSTS_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'posts'))
    TEMPLATES_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, 'templates'))
    CONFIG_FILE = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'site.yaml'))
    MEDIA_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'media'))
    OUTPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, args.output_dir))
    STYLESHEET_PATH = os.path.normpath(os.path.join(TEMPLATES_DIR, 'style.css'))

    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Load templates
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    post_template = env.get_template('post.html')
    index_template = env.get_template('index.html')

    def split(value, delimiter):
        return value.split(delimiter)

    env.globals['split'] = split

    # Load site configuration
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Get all posts
    posts = []
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(POSTS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Extract title from the first line of the markdown file
                title = lines[0].replace('#', '').strip()
                # Join the rest of the lines
                content = "".join(lines[1:])
                # Generate HTML from markdown
                html_content = markdown.markdown(content, extensions=['fenced_code'])
                # Extract date from filename
                date_str = '_'.join(filename.split('_')[:3])
                date = datetime.strptime(date_str, '%Y_%m_%d')
                # Create a dictionary for each post
                post = {
                    'title': title,
                    'content': html_content,
                    'filename': filename,
                    'html_filename': filename.replace('.md', '.html'),
                    'date': date,
                }
                posts.append(post)

    # Sort posts by date
    posts.sort(key=lambda x: x['date'], reverse=True)

    # Group posts by year
    posts_by_year = {}
    for post in posts:
        year = post['date'].year
        if year not in posts_by_year:
            posts_by_year[year] = []
        posts_by_year[year].append(post)

    # Create individual post pages
    for post in posts:
        with open(os.path.join(OUTPUT_DIR, post['html_filename']), 'w', encoding='utf-8') as f:
            f.write(post_template.render(post=post, config=config))

    # Create index page
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_template.render(posts_by_year=posts_by_year, config=config))

    # Load publications data
    PUBLICATIONS_FILE = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'publications.yaml'))
    with open(PUBLICATIONS_FILE, 'r', encoding='utf-8') as f:
        publications_data = yaml.safe_load(f)

    # Create publications page
    publications_template = env.get_template('publications.html')
    with open(os.path.join(OUTPUT_DIR, 'publications.html'), 'w', encoding='utf-8') as f:
        f.write(publications_template.render(publications=publications_data, config=config))

    # Copy media files
    copy_media(MEDIA_DIR, os.path.join(OUTPUT_DIR, 'media'))
    # Copy stylesheet
    copy_stylesheet(STYLESHEET_PATH, os.path.join(OUTPUT_DIR, 'style.css'))

if __name__ == '__main__':
    main()

