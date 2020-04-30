
# *******************************************************************
# This file illustrates how to send a file using an
# application-level protocol where the first 10 bytes
# of the message from client to server contain the file
# size and the rest contain the file data.
# *******************************************************************
import socket
import os
import sys

# Command line checks 
if len(sys.argv) < 2:
	print "USAGE python " + sys.argv[0] + " <FILE NAME>" 

# Server address
serverAddr = sys.argv[1]

# Server listen port
serverPort = int(sys.argv[2])
# Server data port
dataPort = serverPort+1

# Create a TCP socket
controlSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
controlSock.connect((serverAddr, serverPort))

print "Connnected to server"

status = True
while status:

	userinput = str(raw_input("ftp> "))
	if(userinput=="quit"):
		# Close the control socket and the file
		controlSock.close()
		status = False
	elif (userinput.find("get ", 0,4)!= -1):
		print "get Command"
	elif (userinput.find("put ", 0,4)!= -1 and len(userinput)>4):
		# Create a TCP  data socket
		dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Connect to the server
		dataSock.connect((serverAddr, dataPort))

		# The name of the file
		fileName = userinput[4:]
		# Open the file
		fileObj = open(fileName, "r")
		# The number of bytes sent
		numSent = 0

		# The file data
		fileData = None

		# Get the size of the data
		# and convert it to string
		dataMetadata = str(os.path.getsize(fileName))
		sentSize= dataMetadata
		
		# Prepend 0's to the size string
		# until the size is 10 bytes
		while len(dataMetadata) < 10:
			dataMetadata = "0" + dataMetadata
		# Prepend " " to filename untill 31 bytes
		#filename cannot be larger than 31 characters
		while len(fileName) < 31:
			fileName = " " + fileName
		#add filename to metadata
		dataMetadata = dataMetadata + fileName;

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
		print "Sent ", sentSize, " bytes."
	elif (userinput.find("ls", 0,2)!= -1):
		print "ls Command"
	else:
		print "invalid Command"


