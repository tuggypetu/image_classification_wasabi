from image_recieve_tets import classify_image
import glob

test_image_path = 'image_store/car.jpg'

print("Classifying.............")
files = glob.glob('image_store/*.jpg')
print(files)
predicted_class = classify_image(test_image_path)
print(f"Image classified as: {predicted_class}")