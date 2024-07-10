import numpy as np
import sqlite3
from Constants import *


class Model:

    def __init__(self):
        self.cond_prob_flag = []
        self.cond_prob_nonflag = []
        self.p_flag = 0
        self.p_nonflag = 0
        self.unique_words = []
        self.n = 0
        self.d = 0
        self.trained = False

    def train(self):
        con = sqlite3.connect(DATABASE_NAME)
        cur = con.cursor()
        res = cur.execute("SELECT * FROM messages")
        res = res.fetchall()
        con.commit()
        con.close()

        X_raw = []
        Y = []
        for i in res:
            X_raw.append(i[1])
            Y.append(i[3])

        Y = np.array(Y)
        Y_nonzeros = np.count_nonzero(Y)

        if Y_nonzeros == 0 or Y_nonzeros == len(Y):
            print("Dataset cannot be used for training because both positive and negative samples are needed.")
            return

        unique_words = set()
        for i in X_raw:
            for j in i.split(" "):
                unique_words.add(j)
        self.unique_words = list(unique_words)
        self.unique_words.sort()

        self.n = len(X_raw)
        self.d = len(self.unique_words)

        X = np.zeros((self.n, self.d))
        for i_x, x in enumerate(X_raw):
            for i_uw, uw in enumerate(self.unique_words):
                if uw in x:
                    X[i_x][i_uw] = 1

        p_flag = np.count_nonzero(Y)
        p_nonflag = len(Y) - p_flag

        self.p_flag = p_flag / len(Y)
        self.p_nonflag = p_nonflag / len(Y)

        self.cond_prob_flag = []
        self.cond_prob_nonflag = []

        mask_flag = Y == 1
        mask_nonflag = Y == 0

        masked_X_flag = X[mask_flag]
        masked_X_nonflag = X[mask_nonflag]

        for i, uw in enumerate(unique_words):
            p_uw_flag = np.count_nonzero(masked_X_flag[:, i] == 1) / len(masked_X_flag)

            p_uw_nonflag = np.count_nonzero(masked_X_nonflag[:, i] == 1) / len(masked_X_nonflag)

            self.cond_prob_flag.append(p_uw_flag)
            self.cond_prob_nonflag.append(p_uw_nonflag)

        self.trained = True

    def one_hot_encode(self, x_raw):
        x = np.zeros(self.d)
        for i_uw, uw in enumerate(self.unique_words):
            if uw in x_raw:
                x[i_uw] = 1
        return x

    def predict(self, x):
        x = self.one_hot_encode(x)

        p_hat_flag = self.p_flag
        p_hat_nonflag = self.p_nonflag
        print(self.unique_words)
        print(self.cond_prob_nonflag)
        print(self.cond_prob_flag)
        print(x)
        for i, x_i in enumerate(x):
            if x_i == 0:
                p_hat_flag *= 1 - self.cond_prob_flag[i]
                p_hat_nonflag *= 1 - self.cond_prob_nonflag[i]
            else:
                p_hat_flag *= self.cond_prob_flag[i]
                p_hat_nonflag *= self.cond_prob_nonflag[i]

        return p_hat_nonflag, p_hat_flag
