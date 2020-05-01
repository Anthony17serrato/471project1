
# *******************************************************************
# This file illustrates how to send a file using an
# application-level protocol where the first 10 bytes
# of the message from client to server contain the file
# size and the rest contain the file data.
# *******************************************************************
import socket
import os
import sys

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
		controlSock.send("q")
		# Close the control socket and the file
		controlSock.close()
		status = False
	elif (userinput.find("get ", 0,4)!= -1 and len(userinput)>4):
		# The name of the file
		fileName = userinput[4:]
		# Prepend " " to filename untill 31 bytes
		#filename cannot be larger than 31 characters
		while len(fileName) < 31:
			fileName = " " + fileName
		controlSock.send(("g"+fileName))
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

		if(fileSizeBuff == "f"):
			print "Failed: File not on server"
			# Close our side
			clientSock.close()
			#Close data socket
			dataSock.close()
			continue
			
		# Get the file size
		fileSize = int(fileSizeBuff)

		#Recieve the next 31 bytes indicating name of file
		fileNameBuff = ""
		fileNameBuff = recvAll(clientSock, 31)
		
		# Get the file data
		fileData = recvAll(clientSock, fileSize)
		
		# print "The file data is: "
		print "File Downloaded: ", fileNameBuff.strip(), "\nBytes transfered: ", fileSize

		f = open(fileNameBuff.strip(), "w")
		f.write(fileData)
		f.close()
			
		# Close our side
		clientSock.close()
		#Close data socket
		dataSock.close()
	elif (userinput.find("put ", 0,4)!= -1 and len(userinput)>4):
		# The name of the file
		fileName = userinput[4:]
		try:
			# Open the file
			fileObj = open(fileName, "r")
		except IOError:
			print "Failed: file does not exist"
			continue

		controlSock.send("p")
		# Create a TCP  data socket
		dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Connect to the server
		dataSock.connect((serverAddr, dataPort))

		
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
		print "Sent file:", fileName.strip(), "\nSize: ", sentSize, " bytes."
	elif (userinput.find("ls", 0,2)!= -1):
		controlSock.send("l")
		# Receive the first 10 bytes indicating the
		# size of the file
		fileSizeBuff = recvAll(controlSock, 10)
			
		# Get the file size
		fileSize = int(fileSizeBuff)
		cmnd = recvAll(controlSock,fileSize)
		print cmnd
	else:
		print "invalid Command"
