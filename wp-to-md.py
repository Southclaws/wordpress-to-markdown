import sys
import io
import time
import datetime
import dateutil.parser
import re
from bs4 import BeautifulSoup
import html2text
from slugify import slugify
import wget


coderegex1 = re.compile(r'\[sourcecode language=\"[a-zA-Z0-9]*\"\](.*?)\[\/sourcecode\]', re.DOTALL)
coderegex2 = re.compile(r'\[code language=\"[a-zA-Z0-9]*\"\](.*?)\[\/code\]', re.DOTALL)
coderegex3 = re.compile(r'\[code lang=[a-zA-Z0-9]*\](.*?)\[\/code\]', re.DOTALL)


class Post:

	def __init__(self, title, link, date, content, category):
		self.title = title
		self.link = link
		self.date = dateutil.parser.parse(date)
		self.content = content
		self.category = category


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
				item.find('category')['nicename']))

		elif item.find('wp:post_type').string == "attachment":
			attachments.append(item.guid.string)

	return posts, attachments


def gen_markdown(post):

	title = post.title.translate(str.maketrans({"\"": "&#34;",
												":": "&#58;"}))

	header ="""---
layout:     post
title:      "%s"
date:       %s
categories: %s
---
"""%(title, post.date.strftime("%Y-%m-%d %H:%M:%S"), post.category)

	body = re.sub(coderegex1, r"```\n\1```", post.content, re.U)
	body = re.sub(coderegex2, r"```\n\1```", body, re.U)
	body = re.sub(coderegex3, r"```\n\1```", body, re.U)

#	body = html2text.html2text(body)

	return header + body


def save_posts(posts):

	print("> Saving posts!")

	out = ""

	for p in posts:
		print("Saving", p.title, )
		with io.open("_posts/" + p.date.strftime("%Y-%m-%d") + "-" + slugify(p.title) + ".markdown", 'w', encoding='UTF-8') as f:
			f.write(gen_markdown(p))


def download_attachments(attachments):

	print("> Wget'ing attachments!")


def main():

	if len(sys.argv) != 2:
		print("Parameters: filename for wordpress .xml export file")
		return

	filename = sys.argv[1]
	doc = ""
	posts = []
	attachments = []

	doc = load_doc(filename)
	posts, attachments = parse_doc(doc)

	save_posts(posts)
	download_attachments(attachments)


if __name__ == '__main__':
	main()
