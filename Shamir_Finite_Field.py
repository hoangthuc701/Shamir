import random
import sys
import numpy as np

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
    
    def __init__(self,p):
        self.calculator = Calculator(p)
    
    def extract(self,k, numbers):
        a = np.zeros((k,k+1))
        for i in range(1,k+1):
            for j in range(k,0,-1):
                a[i-1,k-j] = self.calculator.pow(i,j-1)
            a[i-1][k] = numbers[i-1]
        coefficients =  self.gaussSolver(k,a)

        return int(round(coefficients[k-1]))

    def extractCoefficients(self,k,numbers):
        a = np.zeros((k,k+1))
        for i in range(1,k+1):
            for j in range(k,0,-1):
                a[i-1,k-j] = self.calculator.pow(i,j-1)
            a[i-1][k] = numbers[i-1]
        coefficients =  self.gaussSolver(k,a)

        for i in range(len(coefficients)):
            coefficients[i] = int(round(coefficients[i])) 
        return coefficients[0:k]

    def gaussSolver(self, n, matrix):
        a = matrix.astype(int)
        x = np.zeros(n+1).astype(int)

        for i in range(n):
            if a[i][i] == 0.0:
                sys.exit('Divide by zero detected!')
                
            for j in range(i+1, n):
                ratio = self.calculator.division(a[j][i],a[i][i])
                
                for k in range(n+1):
                    a[j][k] =  self.calculator.sub(a[j][k],   self.calculator.mul(ratio,a[i][k])    )

        # Back Substitution
        x[n-1] = self.calculator.division(a[n-1][n],a[n-1][n-1])

        for i in range(n-2,-1,-1):
            x[i] = a[i][n]
            
            for j in range(i+1,n):
                x[i] = self.calculator.sub(x[i],self.calculator.mul(a[i][j],x[j]))
            
            x[i] = self.calculator.division(x[i],a[i][i])
        
        return x

    def create(self,s,n,k):
        if k >= n:
            return
        coefficients = [0]*(k-1)
        numbers = [0]
        for i in range(0, k-1):
            value = self.calculator.random()
            while value in numbers:
                value = self.calculator.random()
            numbers.append(value)
            coefficients[i] = value
        
        coefficients.append(s)
        
        # generate share key
        results = []
        for i in range(1,n+1):
            result = self.evaluate(i,coefficients)
            results.append(result)

        return results

    def evaluate(self,number,coefficients):
        result = 0
        n = len(coefficients) - 1
        for i in range(0, len(coefficients)):
            result = self.calculator.sum(result,self.calculator.mul(coefficients[i],self.calculator.pow(number,n)))
            n = n - 1 
        return result

    def generateKeyWithCoefficients(self,n, coefficients):
        # generate share key
        results = []
        for i in range(1,n+1):
            result = self.evaluate(i,coefficients)
            
            results.append(result)

        return results

# s= 60
# n= 10
# k= 8

# shamir = Shamir(p)
# x = shamir.create(s,n,k)
# print(shamir.extract(k,x)==s)