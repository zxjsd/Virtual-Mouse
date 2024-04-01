import cv2
import mediapipe as mp
import pyautogui

# Mediapipe Hands modülünü yükleyin
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
canmove =True

# Video akışı için gerekli özellikler
cap = cv2.VideoCapture(0)  # Varsayılan kamera kullanılıyor, başka bir kaynak için değeri değiştirin

# Video çerçevesi boyutları
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Ekranın boyutları
screen_width, screen_height = pyautogui.size()

# FPS ayarı
desired_fps = 30
cap.set(cv2.CAP_PROP_FPS, desired_fps)

# İlk tıklama kontrolü için flag
clicked = False

# Sağ tıklama kontrolü için flag
right_clicked = False

# Mouse hareketlerini yumuşatmak için önceki parmak konumları
prev_mapped_x = frame_width // 2
prev_mapped_y = frame_height // 2

# Mouse scroll kontrolü için flag
scrolling = False

with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=2) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Frame'i BGR'den RGB'ye dönüştürün
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Mediapipe ile el tespiti yapın
        results = hands.process(image)

        # El tespiti başarılıysa
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Hands modülünün çizim fonksiyonunu kullanarak elin noktalarını ve bağlantılarını çizin
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Başparmak ve işaret parmağı pozisyonlarını alın
                thumb_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * frame_width
                thumb_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * frame_height
                index_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * frame_width
                index_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * frame_height
                middle_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * frame_height
                middle_x = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * frame_width
                ring_x = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x * frame_width
                ring_y = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y * frame_height
                pinky_x = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].x * frame_width
                pinky_y = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y * frame_height

                # Parmağın pozisyonunu kameranın görüş açısından ekran koordinatlarına dönüştürün
                mapped_x = int(screen_width - (pinky_x/ frame_width) * screen_width)
                mapped_y = int((pinky_y / frame_height) * screen_height)

                # Mouse hareketlerini yumuşatmak için önceki konumları kullanarak güncel konumu belirleyin
                mapped_x = prev_mapped_x * 0.5 + mapped_x * 0.5
                mapped_y = prev_mapped_y * 0.5 + mapped_y * 0.5

                if(canmove==True):
                    pyautogui.moveTo(mapped_x, mapped_y)

                # Eğer parmak ekranın en tepesine ulaşırsa, mouse'u da oraya taşı
                if mapped_y == 0:
                    pyautogui.moveTo(mapped_x, 0)
                
                # Eğer parmak ekranın soluna ulaşırsa, mouse'u da oraya taşı
                if mapped_x == 0:
                    pyautogui.moveTo(0, mapped_y)

                # Tıklama işlemi
                if cv2.norm((thumb_x, thumb_y), (index_x, index_y)) < 0.05 * frame_width and not clicked:
                    pyautogui.click()
                    clicked = True
                elif cv2.norm((thumb_x, thumb_y), (index_x, index_y)) >= 0.05 * frame_width:
                    clicked = False

                # Sağ tıklama işlemi
                if cv2.norm((middle_x, middle_y), (index_x, index_y)) < 0.03 * frame_width and not right_clicked:
                    pyautogui.rightClick()
                    right_clicked = True
                elif cv2.norm((middle_x, middle_y), (index_x, index_y)) >= 0.03 * frame_width:
                    right_clicked = False

                # Mouse scroll işlemi
                if cv2.norm((middle_x, middle_y), (thumb_x,thumb_y)) < 0.03 * frame_width:
                    
                    pyautogui.scroll(10)  # Scroll up
                    canmove =False
                elif cv2.norm((ring_x,ring_y), (thumb_x,thumb_y)) < 0.03 * frame_width:
                   
                    pyautogui.scroll(-10)  # Scroll down
                    canmove =False
                else:
                    canmove =True  # Reset scrolling flag if hand is not moving for scrolling

                # Önceki konumları güncelle
                prev_mapped_x = mapped_x
                prev_mapped_y = mapped_y

        # İskeleti çıkarmış olan çerçeveyi gösterin
        cv2.imshow('Hand Skeleton', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows() 