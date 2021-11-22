import random
import sys
import numpy as np
from sklearn.utils import shuffle

class Calculator:
    def __init__(self,p):
        self.p = p

    def sum(self,a,b):
        return (a%self.p+b%self.p)%self.p
    def sub(self,a,b):
        return self.sum(a,-b)
    def mul(self,a,b):
        return ((a%self.p)*(b%self.p))%self.p
    
    def division(self,a,b):
        return self.mul(a,self.modinv(b))
    
    def pow(self,a,b):
        result = 1
        for i in range(b):
            result = result*a%self.p
        return result%self.p
    
    def egcd(self,a, b):
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = self.egcd(b % a, a)
            return (g, x - (b // a) * y, y)

    def modinv(self,a):
        g, x, y = self.egcd(a, self.p)
        if g != 1:
            raise Exception('modular inverse does not exist')
        else:
            return x % (self.p)
    def random(self):
        return random.randint(0, self.p)%self.p
    
class Shamir:

    def __init__(self, p):
        self.cal = Calculator(p)
    
    def join(self,xs,ys,k):
        '''
        Tái tạo tin mật s từ n' phần của tin mật (n' >= k).

        Các tham số:
        xs, ys (2 mảng numpy một chiều, len = n'): n' phần của tin mật: phần thứ 1 là (xs[0], ys[0]), 
                                                                        phần thứ 2 là (xs[1], ys[1]), 
                                                                        ...
        k (int): Ngưỡng k mà đã dùng khi phân chia tin mật.
        Giá trị trả về:
            int: Tin mật s được tái tạo,
                trong trường hợp không đủ số phần để tái tạo tin mật thì trả về None.        

        '''
        if len(xs) < k:
            return None

        matrix = np.zeros((k,k+1))
        for i in range(0,min(k, len(xs))):
            for j in range(k,0,-1):
                matrix[i,k-j] = self.cal.pow(xs[i],j-1)
            matrix[i][k] = ys[i]
        try: 
            coefficients =  self.solver(k,matrix)
        except:
            return None
        return int(round(coefficients[k-1]))

    def findAllCoefficients(self,xs,ys,k):
        if len(xs) < k:
            return None

        matrix = np.zeros((k,k+1))
        for i in range(0,min(k, len(xs))):
            for j in range(k,0,-1):
                matrix[i,k-j] = self.cal.pow(xs[i],j-1)
            matrix[i][k] = ys[i]
        try: 
            coefficients =  self.solver(k,matrix)
        except:
            return None

        for i in range(len(coefficients)):
            coefficients[i] = int(round(coefficients[i])) 
        return coefficients[0:k]


    def solver(self, n, matrix):
        '''
        Hàm giải ma hàm n ẩn với n phương trình
        
        '''
        a = matrix.astype(float)
        coefs = np.zeros(n+1)
        for i in range(n):
            if a[i][i] == 0.0:
                sys.exit('Divide by zero detected!')
                
            for j in range(i+1, n):
                ratio = self.cal.division(a[j][i],a[i][i])
                
                for k in range(n+1):
                    a[j][k] = self.cal.sub(a[j][k],self.cal.mul(ratio,a[i][k]))

        # Back Substitution
        coefs[n-1] = self.cal.division(a[n-1][n],a[n-1][n-1])

        for i in range(n-2,-1,-1):
            coefs[i] = a[i][n]
            
            for j in range(i+1,n):
                coefs[i] = self.cal.sub(coefs[i],self.cal.mul(a[i][j],coefs[j]))
            
            coefs[i] = self.cal.division(coefs[i],a[i][i])
        
        return coefs

    def split(self,s,n,k):
        '''
        Hàm phân chia tin mật s thành n phần sao cho chỉ khi có ít nhất là k phần (k<=n)
        thì mới tái tạo được s, còn ít hơn k phần thì sẽ không biết gì về s.

        Các tham số:
        s (float): Tin mật cần chia sẻ.
        n (int): Số phần cần phân chia.
        k (int): Ngưỡng k (k <= n).
        Giá trị trả về:
        2 mảng numpy một chiều: Gọi 2 mảng này là xs và ys,
                                n phần được phân chia: phần thứ 1 là (xs[0], ys[0]),
                                                       phần thứ 2 là (xs[1], ys[1]),
                                                       ...
                                với ys[i] = f(xs[i]).

        '''
        if k >= n:
            return
        coefficients = [0]*(k-1)
        numbers = [0]
        for i in range(0, k-1):
            value = self.cal.random()
            while value in numbers:
                value = self.cal.random()
            numbers.append(value)
            coefficients[i] = value
        
        coefficients.append(s)
        
        # generate share key
        xs = []
        ys = []
        for i in range(1,n+1):
            result = self.compute_polynomial(i,coefficients)
            xs.append(i)
            ys.append(result)

        return xs,ys

    def compute_polynomial(self,xs,coefficients):
        '''
        Tính giá trị của hàm đa thức.
        '''
        result = 0
        n = len(coefficients) - 1
        for i in range(0, len(coefficients)):
            result = self.cal.sum(result,self.cal.mul(coefficients[i],self.cal.pow(xs,n)))
            n = n - 1 
        return result
    
    def splitWithCoefficients(self, xs, coefficients):
        ys = []
        for i in range(len(xs)):
            result = self.compute_polynomial(xs[i],coefficients)
            ys.append(result)

        return xs,ys

# Phân chia tin mật 
s = 51
n = 10
k = 1
p = 251

shamir = Shamir(p)
xs, ys = shamir.split(s,n,k)

# Chọn ngẫu nhiên n' phần để tái tạo tin mật

xs1, ys1 = shuffle(xs, ys, random_state = 0)
n_prime = k - 1
rec_s = shamir.join(xs1[:n_prime], ys1[:n_prime], k)
print(rec_s)

n_prime = k
rec_s1 = shamir.join(xs1[:n_prime], ys1[:n_prime], k)
print(rec_s1)

n_prime = k + 1
rec_s2 = shamir.join(xs1[:n_prime], ys1[:n_prime], k)
print(rec_s2)