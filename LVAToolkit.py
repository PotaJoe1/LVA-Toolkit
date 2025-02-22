import os
from pathlib import Path
from PIL import Image
import math
#Functions
def clear_folder(path): #Clear a folder
    for file in os.listdir(path):
        os.remove(path+"/"+file)

def extract_audio(infile, outfile, qScale): #Extract audio as MP3
    cmd = 'ffmpeg.exe -y -i "'+infile+'" -vn -codec:a libmp3lame -qscale:a '+qScale+' "'+outfile+'.mp3"'
    os.system(cmd)

def extract_video(infile, outfile, scale, rate): #Extract video as PNG sequence
    cmd = 'ffmpeg.exe -y -i "'+infile+'" -vf "scale='+scale+',fps='+outRate+'" -sws_flags lanczos "'+outfile+'%08d.png"'
    os.system(cmd)

def convert_lvg(infile, compression, linelen, colmode): #Convert an image file to LVG
    minLineLength = linelen
    inImg = Image.open(infile).convert("RGBA")
    imgData = list(inImg.getdata())
    outputData = []
    outputList = []
    lineLength = 0
    lastR = 999
    lastG = 999
    lastB = 999
    lastA = 999
    if colmode == "RGBA8":
        chunksize = 24
    if colmode == "RGBA4":
        chunksize = 41
    if colmode == "LA8":
        chunksize = 41
    if colmode == "LA4":
        chunksize = 62
    for pixel in imgData:
        if pixel[0] < lastR + compression and pixel[0] > lastR - compression and pixel[1] < lastG + compression and pixel[1] > lastG - compression and pixel[2] < lastB + compression and pixel[2] > lastB - compression and pixel[3] < lastA + compression and pixel[3] > lastA - compression and lineLength < 255: #If colours are close enough
            lineLength += 1
        elif lineLength < minLineLength:
            lineLength += 1
        else: #If it's too different
            lastR = pixel[0]
            lastG = pixel[1]
            lastB = pixel[2]
            lastA = pixel[3]

            if colmode == "RGBA8":
                addcol = (str("{:02x}".format(int(pixel[0]))))+(str("{:02x}".format(int(pixel[1]))))+(str("{:02x}".format(int(pixel[2]))))+(str("{:02x}".format(int(pixel[3]))))+(str("{:02x}".format(int(lineLength))))
            if colmode == "RGBA4":
                addcol = (str("{:01x}".format(int(pixel[0]/16))))+(str("{:01x}".format(int(pixel[1]/16))))+(str("{:01x}".format(int(pixel[2]/16))))+(str("{:01x}".format(int(pixel[3]/16))))+(str("{:02x}".format(int(lineLength))))
            if colmode == "LA8":
                addcol = (str("{:02x}".format(int((pixel[0]+pixel[1]+pixel[2])/3))))+(str("{:02x}".format(int(pixel[3]))))+(str("{:02x}".format(int(lineLength))))
            if colmode == "LA4":
                addcol = (str("{:01x}".format(int(((pixel[0]+pixel[1]+pixel[2])/3)/16))))+(str("{:01x}".format(int(pixel[3]/16))))+(str("{:02x}".format(int(lineLength))))

            outputData.append(addcol)
            if len(outputData) > chunksize:
                outputList.append("".join(outputData))
                outputData = []
            lineLength = 1
    outputList.append("".join(outputData))
    return(outputList)

def convert_lva(inFolder, compression, resX, resY, fps, linelen, colmode): #Convert a folder into LVA
    outputLVA = [resX, resY, fps, colmode]
    currentFrame = 0
    for file in os.listdir(inFolder):
        currentFrame += 1
        outputLVA.append("FRAME_"+str(currentFrame))
        filePath = inFolder+"/"+file
        outputLVA += convert_lvg(filePath, compression, linelen, colmode)
    return(outputLVA)

def difference_check(inFolder, outFolder, resX, resY, compression):
    totalPix = int(resX) * int(resY)
    img2Data = [(0,0,0)] * totalPix
    for file in os.listdir(inFolder):
        checkedData = []
        img1 = Image.open(inFolder+"/"+file).convert("RGB")
        img1Data = list(img1.getdata())
        currentPix = 0
        for pixel in img1Data:
            if pixel[0] < img2Data[currentPix][0] + compression and pixel[0] > img2Data[currentPix][0] - compression and pixel[1] < img2Data[currentPix][1] + compression and pixel[1] > img2Data[currentPix][1] - compression and pixel[2] < img2Data[currentPix][2] + compression and pixel[2] > img2Data[currentPix][2] - compression:
                checkedData.append((0,0,0,0))
            else:
                checkedData.append((pixel[0],pixel[1],pixel[2],255))
                img2Data[currentPix] = (pixel[0],pixel[1],pixel[2])
            currentPix += 1
        outImg = Image.new("RGBA", (int(resX),int(resY)))
        outImg.putdata(checkedData)
        outImg.save(outFolder+"/"+file)
        outImg.close()
    img1.close()

#Startup
print("Clearing temp folder...")
clear_folder("temp/diffcheck")
clear_folder("temp/frames")
choice = input("LVA TOOLKIT Version 2.4\n2024-2025 PotaJoe\n\n1 - Video to LVA\n2 - Image to LVG\n3 - Help\n")
if choice == "1":
    inVid = input("Input Video: ")
    colourMode = input ("Output Colour Mode: ")
    outResX = input("Output Resolution X: ")
    outResY = input("Output Resolution Y: ")
    outRate = input("Output Framerate: ")
    compLevel = int(input("Colour Compression Level: "))
    minlen = int(input("Minimum Line Length: "))
    diffLevel = int(input("Motion Compression Level: "))
    aQuality = input("Audio Quality: ")
    print("Extracting audio...")
    extract_audio(inVid, "outputs/"+Path(inVid).stem, aQuality)
    print("Extracting frames...")
    extract_video(inVid, "temp/frames/frame", outResX+":"+outResY, outRate)
    print("Applying difference check...")
    difference_check("temp/frames", "temp/diffcheck", outResX, outResY, diffLevel)
    print("Converting to LVA...")
    outLVA = convert_lva("temp/diffcheck", compLevel, outResX, outResY, outRate, minlen, colourMode)
    print ("Reformatting LVA...")
    outString = "\n".join(outLVA) + "\n"
    print ("Writing to file...")
    file = open("outputs/"+Path(inVid).stem+".txt", "w")
    file.write(outString)
    file.close()
    print("Done!\n")
if choice == "2":
    inImg = input("Input Image: ")
    colourMode = input ("Output Colour Mode: ")
    compLevel = int(input("Colour Compression Level: "))
    minlen = int(input("Minimum Line Length: "))
    print("Converting to LVG...")
    outLVG = convert_lvg(inImg, compLevel, minLen, colourMode)
    print ("Reformatting LVG...")
    outString = "\n".join(outLVG) + "\n"
    print ("Writing to file...")
    file = open("outputs/"+Path(inImg).stem+".txt", "w")
    file.write(outString)
    file.close()
    print("Done!\n")
if choice == "3":
    choice = input("1 - What is LVA?\n2 - Converting to LVG\n3 - Converting to LVA\n4 - Compression Settings\n5 - Colour Modes\n")
    if choice == "1":
        print("LVA stands for Line Variation Animation. It's a video format that stores frames as a series of lines with different colours and lengths, grouping lines of similar pixels together to reduce the total filesize of the frame.")
        print("The goal of LVA is to store decently compressed full-motion video in a way where the code required for playback is extremely lightweight.")
        print("It's primary use case is in Scratch projects, which while extremely limiting in size and speed, can use pen blocks to draw lines extremely quickly and efficiently.\n")
    if choice == "2":
        print("Option 2 on the main screen is the LVG converter. This tool will convert an image file into a static LVG image.\nYour input image should be in the same folder as this program. Make sure to include the extension while typing it in.\nOnce you've input your file and compression settings, the program will begin the LVG conversion.\nOnce it's done, you'll be able to find your file as a .txt in the outputs folder.")
    if choice == "3":
        print("Option 1 on the main screen is the LVA converter. This tool will convert a video file into an LVA animation.\nYour input video should be in the same folder as this program. Make sure to include the extension while typing it in.\nOnce you've input your file and compression settings, the program will use a pixel difference check to compress the animation's frame data. This will take a while.\nOnce the difference check is done, it will convert the frames into LVG, then pack them into LVA. This can also take a while.\nOnce it's done, you'll be able to find your file as a .txt in the outputs folder, alongside a .mp3 of the audio.")
    if choice == "4":
        print("-Colour Compression Level\nThis value controls how different colours have to be for the program to make a new line.\nLarger numbers lead to better compression, but lower detail.\nValues between 16-32 tend to give a good balance.\nMinimum Value: 0 | Maximum Value: 255\n")
        print("-Minimum Line Length\nThis value controls the minimum length the current line must be before a new one is made.\nLarger numbers can improve compression on detailed images and LVAs, but can greatly reduce detail and cause a streaky blur effect.\nValues between 2-4 are usually not too noticeable.\nMinimum Value: 0 | Maximum Value: 255\n")
        print("-Motion Compression Level [LVA Only]\nThis value controls how different colours need to be per-frame for the pixels to be kept.\nLarger numbers can improve compression, but cause ghosting and trailing.\nThis setting may increase filesize if the minimum line length is set too low and/or there's too much movement.\nIt's reccomended to keep this setting at 2 or below.\nMinimum Value: 0 | Maximum Value: 255\n")
        print("-Audio Quality [LVA Only]\nThis value controls the quality of the output MP3 audio.\nHigher values give smaller audio files at the cost of audio quality.\nYou won't really need to go above 5 unless you have a lot of other audio in your project.\nMinimum Value: 1 | Maximum Value: 9\n")
        print("-Colour Mode\nThis value selects the colour mode, which provides another tradeoff between filesize and quality.\n")
    if choice == "5":
        print("-RGBA8\nFull colour + Alpha, 8 bits per channel, 24 bits per pixel.\n")
        print("-RGBA4\nFull colour + Alpha, 4 bits per channel, 16 bits per pixel.\n")
        print("-LA8\nGreyscale + Alpha, 8 bits per channel, 16 bits per pixel.\n")
        print("-LA4\nGreyscale + Alpha, 4 bits per channel, 8 bits per pixel.\n")
input("Press ENTER to close the program.")
