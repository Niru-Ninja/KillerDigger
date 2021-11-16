from PIL import Image
import array


directory = input(" filename: ")
image = Image.open(directory)
width, height = image.size

bitValue = "0" #Value in bit of the pixel we are reading.
bitChain = ""  #Chain to accumulate a byte and make a character.
data = array.array('B')
with open("mapResult", "wb") as file:
	for bitY in range(height):
		for bitX in range(width):
			color = image.getpixel((bitX,bitY))
			colorIndex = color[0] + color[1] + color[2]
			if colorIndex > 24:
				bitValue = "1"
			else:
				bitValue = "0"
			bitChain += bitValue
			if len(bitChain) >= 8:
				data.append(int(bitChain, 2))
				bitChain = ""
	data.tofile(file)