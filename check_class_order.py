from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_dir = "dataset/prepared/train"

datagen = ImageDataGenerator(rescale=1./255)
gen = datagen.flow_from_directory(train_dir)
print("Class indices:", gen.class_indices)
