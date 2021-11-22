import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import shape
from Shamir_Finite_Field import Shamir

def get_file_name(path):
    if not os.path.isdir(path):
        return os.path.splitext(os.path.basename(path))[0].split(".")[0]

def generate_image(image_file, n, k):

    print("Start")
    p = 251

     # khởi tạo 
    shamir = Shamir(p)

    print("Running....")

    img = Image.open(image_file)
    img__tmp_pixels = np.array(img)

    # nếu kích thước thì sẽ resize lại để chia hết cho k 
    new_image_size = img__tmp_pixels.shape[1]
    if img__tmp_pixels.shape[1] % k != 0:
        new_image_size = int(img__tmp_pixels.shape[1]/k + 1)*k

    img_pixels =  np.zeros(shape=(img__tmp_pixels.shape[0],new_image_size))

    # chuyển sang mảng mơi
    for r in range(img__tmp_pixels.shape[0]):
        for c in range(img__tmp_pixels.shape[1]):
            img_pixels[r][c] = img__tmp_pixels[r][c]

    # Với các pixel có giá trị > 250, đổi giá trị thành 250
    for r in range(img_pixels.shape[0]):
        for c in range(img_pixels.shape[1]):
            if img_pixels[r][c] > 250:
                img_pixels[r][c] = 250

    # mảng lưu các hình ảnh kết quả
    if (img_pixels.shape[1] % k == 0):
        add_one = 0
    else:
        add_one = 1
    img_result_pixels=[]
    for i in range(n):
        img_result_pixels.append(np.zeros(shape=(img_pixels.shape[0],int( add_one + img_pixels.shape[1]/k))))
    
    xs = np.arange(1,n+1)
    # duyệt các pixel theo thứ tự từng dòng, mỗi dòng duyệt tiếp k....

    for r in range(img_pixels.shape[0]):
        for c in range(0,img_pixels.shape[1],k):
            coefficients=img_pixels[r][c:c+k] 
            _ , share_keys = shamir.splitWithCoefficients(xs,coefficients)

            # ghép key cho từng ảnh
            for i in range(n):
                img_result_pixels[i][r][int(c/k)] = share_keys[i]

    # ghi các file ảnh xuống thành từng file
    for i in range(n):
        image = Image.fromarray(img_result_pixels[i]).convert('L')
        
        image.save("./results/"+str(xs[i])+".bmp")

    print("Done")


def removePading(images, k ):
    width = images.shape[1]
    height = images.shape[0]

    number_of_0 = images.shape[1]
    for r in range(0, height):
        i = width - 1
        num0 = 0
        while images[r][i] == 0:
            i = i - 1
            num0 = num0 + 1
        number_of_0 = min(number_of_0, num0)
    y_heigh = width - number_of_0
    y_low = 0
    x_low = 0
    x_heigh = height
    return images[x_low:x_heigh,y_low:y_heigh]

def findImageSize(n,images):
    i = 0
    while i< n and images[i] == []:
        i = i + 1

    if (i>=n):
        return (0,0)
    return (images[i].shape[0],images[i].shape[1])

def reproduction_image(folder, n, k , extr_image_file):    
    print("Start")
    p = 251

     # khởi tạo 
    shamir = Shamir(p)
    print("Running....")

    # Khởi tạo mảng để lưu 
    img_pixels = []
    xs = [] 
    with os.scandir(folder) as entries:
        for entry in entries:
            img_pixels.append(np.array(Image.open(folder +"/"+entry.name)))
            xs.append(int(get_file_name(entry.name)))

    img_width, image_height = findImageSize(n, img_pixels)
    original_image = np.zeros(shape=(img_width,image_height*k))
    
    # duyệt ảnh
    for r in range(img_width):
        for c in range(image_height):
            values = []
            for i in range(len(xs)):
                values.append(img_pixels[i][r][c])
            
            result = shamir.findAllCoefficients(xs,values,k)

            # gán vào ảnh để khôi phục ảnh gốc
            for j in range(k):
                original_image[r][c*k+j] = result[j] 

    # xử lý các phần tử 0 thừa ở phía cuối array lúc thêm vào
    original_image = removePading(original_image, k)
    print(original_image.shape)

    image = Image.fromarray(original_image.astype(np.uint8))
    # np.savetxt('reproduction_image.txt', original_image.astype(int) , fmt='%s', delimiter=',')
    image.save(extr_image_file)
    # lưu ảnh xuóng
    print("Done")

# generate_image('./lena.bmp',10,6)
reproduction_image('./results',10, 6,'reproduction_lena.bmp')