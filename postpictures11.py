#!/usr/bin/env python
# -*- coding: utf-8 -*-
# jen was here

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.methods.posts import GetPost, EditPost, DeletePost, GetPostFormats, GetPostTypes
from datetime import datetime
from HTMLParser import HTMLParser
import urllib
import os.path
import os
import time

client = Client('http://nomorebuttshots.com/xmlrpc.php','egilbert@alum.mit.edu','KRkI8V3zo!EH*7cC$Qz$whOs')

#--------------------------
#Function to load pictures from gopro to local folder
while True:
	try:
		response = urllib.urlopen('http://10.5.5.9:8080/videos/DCIM/101GOPRO/')
		html = response.read() 
		print "Good GoPro Connection"
		break
	except IOError:
		print "No GoPro Connection"
		time.sleep(2)
		continue
		
class MyHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		# Only parse the 'anchor' tag.
		if tag == "a":
		# Check the list of defined attributes.
			for name, value in attrs:
				# If href is defined, print it.
				if name == "href" and value !="?order=N" and value !="?order=s":
						print 'picture found'
						self.output=value #return the path+file name of the image
				        #print value
						#get image name 
						IMAGE = value
						print 'Picture:'+IMAGE
						#compare it to images in Pictures and OldPictures folders
						if os.path.exists(os.path.join('Pictures',IMAGE)) | os.path.exists(os.path.join('OldPictures',IMAGE)):
							#do nothing with image, because it's already in Pictures or OldPictures folders
							print 'Picture already in folder'
						else:
							#if in neither folder already, load to Pictures folder
							urllib.urlretrieve('http://10.5.5.9:8080/videos/DCIM/101GOPRO/'+IMAGE, os.path.join('Pictures',IMAGE))
							print 'New Picture'

#--------------------------------

#check Pictures folder every 1 minute for new pictures (can change time if needed)
while True:
	#run function to move new pics from gopro to local Pictures folder
	while True:
		try:
			response = urllib.urlopen('http://10.5.5.9:8080/videos/DCIM/101GOPRO/')
			html = response.read() 
			print "Good GoPro Connection"
			break
		except IOError:
			print "No GoPro Connection"
			time.sleep(2)
			continue
		
	parser = MyHTMLParser()
	parser.feed(html)
	#delete pics from gopro?
	#check how many files are in Pictures folder
	path = 'Pictures'
	num_files = len([f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))])
	print num_files

	#if >0, choose oldest file and upload to website. Continue until folder is empty
	while num_files>0:
		os.chdir(path)
		files = sorted(os.listdir(os.getcwd()), key=os.path.getctime)
		oldest = files[0]
		#print oldest

		# set to the path to your file
		filename =  oldest
	
		# prepare metadata
		data = {
			'name': oldest,
			'type': 'image/jpg',  # mimetype
		}

		# read the binary file and let the XMLRPC library encode it into base64
		with open(filename, 'rb') as img:
			data['bits'] = xmlrpc_client.Binary(img.read())

		response = client.call(media.UploadFile(data))
		attachment_id = response['id']
		#print 'Attachment ID:', attachment_id

		#find date and time for title of picture
		i = datetime.now()
		gym = 'BKB '
		print i.strftime('%b %d %X')

		#Create post
		post = WordPressPost()
		post.post_type = 'sell_media_item'
		post.title = gym + i.strftime('%b %d %X')
		post.post_status = 'publish'
		post.thumbnail = attachment_id
		post_id = post.id = client.call(posts.NewPost(post))

		#move file from Pictures folder to UploadedPictures folder
		os.chdir('..')
		os.rename(os.path.join(path,oldest), os.path.join('OldPictures',oldest))
		#update num_files
		num_files = len([f for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))])
		#print num_files
		#cycle back so system is while loop
		
	#add time delay of 1 min so code runs continuously
	time.sleep(60) # wait 1 minute 

