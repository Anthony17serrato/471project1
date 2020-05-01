
# *****************************************************
# This file implements a server for receiving the file
# sent using sendfile(). The server receives a file and
# prints it's contents.
# *****************************************************

import socket
import sys
import os
import commands

# The port on which to listen
listenPort = int(sys.argv[1])
#data port
dataPort = listenPort+1

# Create a control socket. 
controlSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
controlSock.bind(('', listenPort))

# Start listening on the socket
controlSock.listen(1)



print "The server control is ready to recieve..."
print "Waiting for connections..."
clientControlSock, addrControl = controlSock.accept()

print "Accepted control connection from client: ", addrControl
print "\n"



# ************************************************
# Receives the specified number of bytes
# from the specified socket
# @param sock - the socket from which to receive
# @param numBytes - the number of bytes to receive
# @return - the bytes received
# *************************************************
def recvAll(sock, numBytes):

	# The buffer
	recvBuff = ""
	
	# The temporary buffer
	tmpBuff = ""
	
	# Keep receiving till all is received
	while len(recvBuff) < numBytes:
		print "recieving..."
		# Attempt to receive bytes
		tmpBuff =  sock.recv(numBytes)
		
		# The other side has closed the socket
		if not tmpBuff:
			break
		
		# Add the received bytes to the buffer
		recvBuff += tmpBuff
	
	return recvBuff
		
# Accept connections forever
while True:
	#recieve first byte which contains the command
	cmnd = recvAll(clientControlSock,1)

	if(cmnd == "l"):
		listoffiles = ""
		# Run ls command, get output, and print it
		for line in commands.getstatusoutput('ls -l'):
			listoffiles = listoffiles + "\n" + str(line)
		sizeofresponse = str(len(listoffiles))
		# Prepend 0's to the size string
		# until the size is 10 bytes
		while len(sizeofresponse) < 10:
			sizeofresponse = "0" + sizeofresponse
		listoffiles = sizeofresponse + listoffiles
		clientControlSock.send(listoffiles)
	
	elif(cmnd == "p"):	
		#create data socket.
		dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Bind the socket to the port
		dataSock.bind(('', dataPort))

		# Start listening on the socket
		dataSock.listen(1)

		# Accept connections
		clientSock, addr = dataSock.accept()
		
		print "Accepted data connection from client: ", addr
		print "\n"

		
		# The buffer to all data received from the
		# the client.
		fileData = ""
		
		# The temporary buffer to store the received
		# data.
		recvBuff = ""
		
		# The size of the incoming file
		fileSize = 0	
		
		# The buffer containing the file size
		fileSizeBuff = ""
		
		# Receive the first 10 bytes indicating the
		# size of the file
		fileSizeBuff = recvAll(clientSock, 10)
			
		# Get the file size
		fileSize = int(fileSizeBuff)
		
		print "The file size is ", fileSize

		#Recieve the next 31 bytes indicating name of file
		fileNameBuff = ""
		fileNameBuff = recvAll(clientSock, 31)
		
		# Get the file data
		fileData = recvAll(clientSock, fileSize)
		
		# print success
		print "SUCCESS: File Uploaded..."

		f = open(fileNameBuff.strip(), "w")
		f.write(fileData)
		f.close()
			
		# Close our side
		clientSock.close()
		#Close data socket
		dataSock.close()
	elif(cmnd == "g"):
		#recieve the next 31 bytes which contain the name of the file to be returned
		fileNameBuff = recvAll(clientControlSock, 31)

		# Create a TCP  data socket
		dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Connect to the client
		dataSock.connect((addrControl[0], dataPort))
		try:
			# Open the file
			fileObj = open(fileNameBuff.strip(), "r")
		except IOError:
			print "FALURE: File does not exist"
			dataSock.send("f")
			dataSock.close()
			continue
		# The number of bytes sent
		numSent = 0

		# The file data
		fileData = None

		# Get the size of the data
		# and convert it to string
		dataMetadata = str(os.path.getsize(fileNameBuff.strip()))
		sentSize= dataMetadata
		
		# Prepend 0's to the size string
		# until the size is 10 bytes
		while len(dataMetadata) < 10:
			dataMetadata = "0" + dataMetadata
		#add filename to metadata
		dataMetadata = dataMetadata + fileNameBuff;

		# Keep sending until all is sent
		while True:
	
			# Read data
			fileData = fileObj.read(1024)
	
			# Make sure we did not hit EOF
			if fileData:
				# Prepend the size of the data to the
				# file data.
				fileData = dataMetadata + fileData	
				dataMetadata=""
		
				# The number of bytes sent
				numSent = 0
		
				# Send the data!
				while len(fileData) > numSent:
					numSent += dataSock.send(fileData[numSent:])
	
			# The file has been read. We are done
			else:
				break
		fileObj.close()
		dataSock.close()
		print "SUCCESS: Sent ", sentSize, " bytes."
	elif(cmnd == "q"):
		# Close our side
		clientControlSock.close()
		print "closed connection from client",addrControl
		print "Waiting for connections..."
		clientControlSock, addrControl = controlSock.accept()

		print "Accepted control connection from client: ", addrControl
		print "\n"
		
