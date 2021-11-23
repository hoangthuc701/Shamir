import numpy as np
import os
import sys
from PIL import Image
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import shape
from Shamir_Finite_Field import Shamir

def removeRedundantColumn(images):
    '''
    Hàm loại bỏ các cột số 0 ở phía cuối ảnh
    '''
    width = images.shape[1]
    height = images.shape[0]

    # đếm số lượng các số 0 được thêm vào lúc chia hình
    number_of_0 = images.shape[1]
    for r in range(0, height):
        i = width - 1
        num0 = 0
        while images[r][i] == 0:
            i = i - 1
            num0 = num0 + 1
        number_of_0 = min(number_of_0, num0)


    # tính toán lại kích thước của ảnh ban đầu
    y_heigh = width - number_of_0
    y_low = 0
    x_low = 0
    x_heigh = height
    return images[x_low:x_heigh,y_low:y_heigh]

def get_file_name(path):
    '''
    Hàm lấy filename khi truyền vào tên file và extension
    '''
    if not os.path.isdir(path):
        return os.path.splitext(os.path.basename(path))[0].split(".")[0]


def convertListToNpArray(list, k):
    '''
    Hàm chuyển từ định dạng list sang nparray. Và tính toán lại kích thước của tấm hình.
    '''

    # tính toán dòng có chiều dài lớn nhất
    max_len = 0
    for i in range(len(list)):
        if len(list[i]) > max_len:
            max_len = len(list[i])


    # tính toán thêm kích thước cần thêm để có thể chiều dài chia hết cho k
    if max_len % k == 0:
        add_more = 0 
    else:
        add_more = k - max_len % k
    # khỏi tạo kích thước của tấm hình mới
    result = np.zeros(shape=(len(list),int( add_more + max_len)))

    # chuyển list dang dạng np.array
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

    # đọc ảnh và chuyển sang dạng np.array
    img = Image.open(image_file).convert('L')
    img_original_pixels = np.array(img)
    img_process = [] 
    
    # khỏi tại xs
    xs = np.arange(1,n+1)

    # Với các pixel có giá trị > 250, đổi giá trị thành 250 và phần còn lạ ở ô kế bên cạnh
    for r in range(img_original_pixels.shape[0]):
        img_process.append([])
        for c in range(img_original_pixels.shape[1]):
            if img_original_pixels[r][c] >= 250:
                img_process[r].append(250)
                img_process[r].append(img_original_pixels[r][c] - 250)
            else:
                img_process[r].append(img_original_pixels[r][c])
    
    img_pixels = convertListToNpArray(img_process,k)

    # toán lại kích thước mới của các ảnh khi split ra
    split_image_width = int(img_pixels.shape[1] / k) 
    if (img_pixels.shape[1] % k != 0):
        split_image_width = split_image_width + 1


    # tạo n 2d np.array để lưu các ảnh split ra
    img_result_pixels=[]
    for i in range(n):
        img_result_pixels.append(np.zeros(shape=(img_pixels.shape[0],split_image_width)))
    
    # duyệt các pixel theo thứ tự từng dòng
    for r in range(img_pixels.shape[0]):
        # với mỗi dòng ta duyệt từng nhóm k
        for c in range(0,img_pixels.shape[1],k):
            coefficients=img_pixels[r][c:c+k]
            # tính toán share_keys cho từng ảnh
            _ , share_keys = shamir.splitWithCoefficients(xs,coefficients)

            # ghép key cho từng ảnh
            for i in range(n):
                img_result_pixels[i][r][int(c/k)] = share_keys[i]

    # ghi các file ảnh xuống thành từng file
    for i in range(n):
        image = Image.fromarray(img_result_pixels[i]).convert('L')
        image.save("./results/"+str(xs[i])+".bmp")

    print("Done")

def findImageSize(images):
    '''
    Hàm lấy kích thước của hình ảnh
    '''
    return (images[0].shape[0],images[0].shape[1])

def reproduction_image(folder, n, k , extr_image_file):    
    print("Start")
    p = 251

     # khởi tạo shamir để tính toán
    shamir = Shamir(p)
    print("Running....")

    # Khởi tạo mảng để lưu 
    img_pixels = []*n
    xs = []

    # Ta tiến hành duyệt tất cả các file ảnh
    with os.scandir(folder) as entries:
        for entry in entries:
            img_pixels.append(np.array(Image.open(folder +"/"+entry.name)))
            # hiện tại em cài đặt tên file sẽ là xs[i], nên lấy tên file lưu vào mảng xs
            xs.append(int(get_file_name(entry.name)))
    
    # nếu số ảnh truyền vào ít hon
    if (len(xs)<k):
        sys.exit('Number of images must be grater than k!')

    img_width, image_height = findImageSize(img_pixels)
    original_image = np.zeros(shape=(img_width,image_height*k))
    
    # duyệt qua từng ô của ảnh
    for r in range(img_width):
        for c in range(image_height):
            values = []
            for i in range(len(xs)):
                values.append(img_pixels[i][r][c])
            
            # tìm k bit của ảnh cũ
            result = shamir.findAllCoefficients(xs,values,k)

            # gán vào ảnh để khôi phục ảnh gốc
            for j in range(k):
                original_image[r][c*k+j] = result[j] 

    # xử lý lại ảnh trên một ảnh khác
    img_r = 0
    img_c = 0
    result = np.zeros(shape=(img_width,image_height*k))
    for r in range(img_width):
        img_r = r
        img_c = 0
        c = 0
        while c < image_height*k:
            # Nếu giá trị tại tại trí là 250 thì ảnh kết quả ta sẽ = giá trị ô đó  + giá trị ô tiếp theo
            if original_image[r][c] == 250:
                result[img_r][img_c] = original_image[r][c] + original_image[r][c+1]
                c = c + 1
            else:
                # ngược lại nếu dưới 250 thì chỉ cần lấy giá trị tại ô đó
                result[img_r][img_c] = original_image[r][c]
            img_c = img_c + 1
            c = c + 1 

    # xử lý các phần tử 0 thừa ở phía cuối array lúc thêm vào
    result = removeRedundantColumn(result)

    # lưu ảnh đã xử lý xong xuống
    image = Image.fromarray(result.astype(np.uint8))
    image.save(extr_image_file)
    
    print("Done")

n = 8
k = 5
generate_image('./lena.bmp',n,k)
reproduction_image('./results',n, k,'reproduction_lena.bmp')