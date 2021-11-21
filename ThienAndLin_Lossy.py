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
    img_pixels = np.array(img)

    # Với các pixel có giá trị > 250, đổi giá trị thành 250
    for r in range(img_pixels.shape[0]):
        for c in range(img_pixels.shape[1]):
            if img_pixels[r][c] > 250:
                img_pixels[r][c] = 250
    np.savetxt('original_image.txt', img_pixels.astype(int) , fmt='%s', delimiter=',')
    img_original = Image.fromarray(img_pixels)
    img_original.save("original_after_format.gif")
    # mảng lưu các hình ảnh kết quả
    if (img_pixels.shape[1] % k == 0):
        add_one = 0
    else:
        add_one = 1
    img_result_pixels=[]
    for i in range(n):
        img_result_pixels.append(np.zeros(shape=(img_pixels.shape[0],int( add_one + img_pixels.shape[1]/k))))
    

    # duyệt các pixel theo thứ tự từng dòng, mỗi dòng duyệt tiếp k....

    for r in range(img_pixels.shape[0]):
        for c in range(0,img_pixels.shape[1],k):
            coefficients=img_pixels[r][c:c+k]
            share_keys = shamir.generateKeyWithCoefficients(n,coefficients)

            # ghép key cho từng ảnh
            for i in range(n):
                img_result_pixels[i][r][int(c/k)] = share_keys[i]

    # ghi các file ảnh xuống thành từng file
    for i in range(n):
        image = Image.fromarray(img_result_pixels[i])
        
        image.save("./results/"+str(i+1)+".gif")

    print("Done")


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
    img_pixels = [[]]*n
    with os.scandir(folder) as entries:
        for entry in entries:
            img_pixels[int(get_file_name(entry.name)) -1 ] = np.array(Image.open(folder +"/"+entry.name))


    img_width, image_height = findImageSize(n, img_pixels)
    original_image = np.zeros(shape=(img_width,image_height*k))
    
    # duyệt ảnh
    for r in range(img_width):
        for c in range(image_height):
            values = []
            for i in range(n):
                if img_pixels != []:
                    values.append(img_pixels[i][r][c])
            
            result = shamir.extractCoefficients(k,values)

            # # xử lý ở hàng cuối cùng
            # if c == image_height-1:
            #     index = 0
            #     while result[index]==0:
            #         del result[index]

            # gán vào ảnh để khôi phục ảnh gốc
            for j in range(k):
                original_image[r][c*k+j] = result[j] 

    image = Image.fromarray(original_image)
    np.savetxt('reproduction_image.txt', original_image.astype(int) , fmt='%s', delimiter=',')
    image.save(extr_image_file)
    # lưu ảnh xuóng
    print("Done")

generate_image('./lena.gif',10,8)
reproduction_image('./results',10, 8,'reproduction_lena.gif')