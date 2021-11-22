import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import shape
from Shamir_Finite_Field import Shamir

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

def get_file_name(path):
    if not os.path.isdir(path):
        return os.path.splitext(os.path.basename(path))[0].split(".")[0]


def convertListToNpArray(list, k):
    max_len = 0
    for i in range(len(list)):
        if len(list[i]) > max_len:
            max_len = len(list[i])

    if max_len % k == 0:
        add_more = 0 
    else:
        add_more = k - max_len % k
    # chuyển list sang dạng np.array 
    result = np.zeros(shape=(len(list),int( add_more + max_len)))

    for r in range(len(list)):
        for c in range(len(list[r])):
            result[r][c] = list[r][c]

    return result

def generate_image(image_file, n, k):

    print("Start")
    p = 251

     # khởi tạo 
    shamir = Shamir(p)

    print("Running....")

    img = Image.open(image_file)
    img_original_pixels = np.array(img)
    img_process = [] 
    
    np.savetxt('original_image.txt', img_original_pixels.astype(int) , fmt='%s', delimiter=',')

    # Với các pixel có giá trị > 250, đổi giá trị thành 250
    for r in range(img_original_pixels.shape[0]):
        img_process.append([])
        for c in range(img_original_pixels.shape[1]):
            if img_original_pixels[r][c] >= 250:
                img_process[r].append(250)
                img_process[r].append(img_original_pixels[r][c] - 250)
            else:
                img_process[r].append(img_original_pixels[r][c])
    
    img_pixels = convertListToNpArray(img_process,k)

    # mảng lưu các hình sảnh kết quả
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
        image = Image.fromarray(img_result_pixels[i]).convert('L')
        
        image.save("./results/"+str(i+1)+".bmp")

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

    # xử lý lại ảnh
    img_r = 0
    img_c = 0
    result = np.zeros(shape=(img_width,image_height*k))
    for r in range(img_width):
        img_r = r
        img_c = 0
        c = 0
        while c < image_height*k:
            if original_image[r][c] == 250:
                result[img_r][img_c] = original_image[r][c] + original_image[r][c+1]
                c = c + 1
            else:
                result[img_r][img_c] = original_image[r][c]
            img_c = img_c + 1
            c = c + 1 

    image = Image.fromarray(result.astype(np.uint8))
    np.savetxt('reproduction_image.txt', result.astype(int) , fmt='%s', delimiter=',')
    image.save(extr_image_file)
    # lưu ảnh xuóng
    print("Done")

generate_image('./lena.bmp',10,8)
reproduction_image('./results',10, 8,'reproduction_lena.bmp')