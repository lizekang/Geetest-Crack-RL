# -*- coding:utf-8 -*-
import time as time_g
import numpy as np
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
EMAIL = ''
PASSWORD = ''
BORDER = 6
THRESHOLD = 60


class CrackGeetest:
    def __init__(self):
        self.url = 'https://account.geetest.com/login'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.email = EMAIL
        self.password = PASSWORD
        self.time_gap = 0.2
        self.a_gap = 1

        self.v = 0.0
        self.a = 2.0
        self.start = 0.0
        self.end = 100.0
        self.pos = 0.0
        self.time = 0.0
        self.steps = 0
        self.state = [self.start, self.end, self.pos, self.time, self.v, self.a]
        self.track = []
        self.a_track = []
        self.all_reward = []

    def get_geetest_button(self):
        """
        获取初始验证按钮
        :return: 按钮对象
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
        return button

    def get_position(self):
        """
        获取验证码位置
        ::return: 验证码位置元组
        """
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'geetest_canvas_img')))
        time_g.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return slider

    def get_geetest_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print (name, top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def open(self):
        """
        打开网页输入用户名密码
        :return: None
        """
        self.browser.get(self.url)
        email = self.wait.until(EC.presence_of_element_located((By.ID, 'email')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))
        email.send_keys(self.email)
        password.send_keys(self.password)

    def close(self):
        """
        关闭浏览器
        :return: None
        """
        self.browser.close()

    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1: 不带缺口图片
        :param image2: 带缺口图片
        :return:
        """
        left = 60
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i
                    return left
        return left

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = THRESHOLD
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 2
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time_g.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def login(self):
        """
        登录
        :return: None
        """
        submit = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'login-btn')))
        submit.click()
        time_g.sleep(10)
        print(u'登录成功')

    def reset(self):
        # 输入用户名密码
        self.open()
        # 点击验证按钮
        button = self.get_geetest_button()
        button.click()
        # 获取验证码图片
        image1 = self.get_geetest_image('captcha1.png')
        # 点按呼出缺口
        self.slider = self.get_slider()
        self.slider.click()
        # 获取带缺口的验证码图片
        image2 = self.get_geetest_image('captcha2.png')
        # 获取缺口位置
        self.gap = self.get_gap(image1, image2) - BORDER

        # 减去缺口位移
        # self.gap -= BORDER
        print('缺口位置', self.gap)
        if self.gap == 54:
            self.reset()
        self.v = 0.0
        self.a = 2.0
        self.start = 0.0
        self.end = self.gap
        self.pos = 0.0
        self.time = 0.0
        self.state = [self.start, self.end, self.pos, self.time, self.v, self.a]
        self.steps = 0
        self.track = []
        self.all_reward = []
        self.a_track = []
        return self.state

    def step(self, action):
        done = False
        state = self.state
        start, end, pos, time, v, a = state
        if action == 0:
            a0 = a - self.a_gap
        elif action == 1:
            a0 = a
        else:
            a0 = a + self.a_gap
        v0 = v
        v1 = v0 + a0 * self.time_gap
        move = (v1 + v0) / 2 * self.time_gap
        # if move < 0 and pos == 0:
        #     pos = 0
        # else:
        pos += int(move)
        self.track.append(int(move))
        self.a_track.append(a0)
        time += self.time_gap
        if pos > end - 5 and pos < end + 5:
            done = True

        if done:
            # 拖动滑块
            # print(pos)
            print([round(i, 4)for i in self.track])
            self.move_to_gap(self.slider, self.track)
            element = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'geetest_success_radar_tip_content')))
            time_g.sleep(6)
            if '验证成功' in element.text:
                reward = 1000.0
            # elif '怪物' in element.text:
            #     reward = 100.0
            else:
                reward = 0.0
            self.all_reward.append(reward)
            # print([round(i, 4) for i in self.all_reward])
            print(reward)
        else:
            if pos < end and move < 0:
                reward = -1.0
            # elif pos < end * 4 / 5 and a > 0:
            #     reward = 1.0
            # elif pos < end * 4 / 5 and a < 0:
            #     reward = -1.0
            # elif pos > end * 4 / 5 and a > 0:
            #     reward = -1.0
            # elif pos > end * 4 / 5 and a < 0:
            #     reward = 1.0
            else:
                reward = 0.0
            self.all_reward.append(reward)
        self.state = [start, end, pos, time, v1, a0]
        return np.array(self.state), reward, done
