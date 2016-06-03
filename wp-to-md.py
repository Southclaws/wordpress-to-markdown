import sys
import os
import io
import time
import datetime
import dateutil.parser
import re

# for xml parsing
from bs4 import BeautifulSoup

# for converting to markdown
import html2text

# for generatingurl friendly filenames
from slugify import slugify

# for downloading attachments
import wget


# for converting various wordpress code tags to markdown
coderegex1 = re.compile(r'\[sourcecode language=\"[a-zA-Z0-9]*\"\](.*?)\[\/sourcecode\]', re.DOTALL)
coderegex2 = re.compile(r'\[code language=\"[a-zA-Z0-9]*\"\](.*?)\[\/code\]', re.DOTALL)
coderegex3 = re.compile(r'\[code lang=[a-zA-Z0-9]*\](.*?)\[\/code\]', re.DOTALL)


class Post:

	def __init__(self, title, link, date, content, category, status):
		self.title = title
		self.link = link
		self.date = dateutil.parser.parse(date)
		self.content = content
		self.category = category
		self.status = status


def load_doc(filename):

	print("> Loading document!")

	doc = ""
	with io.open(filename, 'r', encoding='UTF-8') as f:
		doc = f.read()

	return doc


def parse_doc(doc):

	print("> Parsing document!")

	posts = []
	attachments = []
	soup = BeautifulSoup(doc, 'html.parser')

	for item in soup.find_all('item'):

		if item.find('wp:post_type').string == "post":
			posts.append(Post(
				item.find('title').string,
				item.find('link').string,
				item.find('wp:post_date').string,
				item.find('content:encoded').string,
				item.find('category')['nicename'],
				item.find('wp:status').string))

		elif item.find('wp:post_type').string == "attachment":
			attachments.append(item.guid.string)

	return posts, attachments


def gen_markdown(post):

	h = html2text.HTML2Text()
	h.unicode_snob = 1
	h.body_width = 0
	h.dash_unordered_list = True

	title = post.title.translate(str.maketrans({"\"": "&#34;", ":": "&#58;"}))
	body = post.content

	header ="""---
layout:     post
title:      "%s"
date:       %s
categories: %s
---
"""%(title, post.date.strftime("%Y-%m-%d %H:%M:%S"), post.category)

	body = re.sub(coderegex1, r"<pre>\1</pre>", body, re.U)
	body = re.sub(coderegex2, r"<pre>\1</pre>", body, re.U)
	body = re.sub(coderegex3, r"<pre>\1</pre>", body, re.U)

	body = h.handle(body)

	return header + body


def save_posts(output, posts):

	print("> Saving posts!")

	out = ""
	directory = ""

	for p in posts:
		if p.status == "publish":
			directory = output + "_posts/"

		elif p.status == "draft":
			directory = output + "_drafts/"

		else:
			directory = output + "_other/"

		if not os.path.exists(directory):
			os.makedirs(directory)

		print("Saving", directory + p.date.strftime("%Y-%m-%d") + "-" + slugify(p.title) + ".markdown")

		with io.open(directory + p.date.strftime("%Y-%m-%d") + "-" + slugify(p.title) + ".markdown", 'w', encoding='UTF-8') as f:
			f.write(gen_markdown(p))


def download_attachments(output, attachments):

	print("> Wget'ing attachments!")
	# todo


def main():

	output = "./"

	if len(sys.argv) == 1:
		print("Parameters: filename for wordpress .xml export file, optional output directory")
		return

	elif len(sys.argv) == 2:
		filename = sys.argv[1]

	elif len(sys.argv) == 3:
		filename = sys.argv[1]
		output = sys.argv[2]

	doc = ""
	posts = []
	attachments = []

	doc = load_doc(filename)
	posts, attachments = parse_doc(doc)

	save_posts(output, posts)
	download_attachments(output, attachments)


if __name__ == '__main__':
	main()
