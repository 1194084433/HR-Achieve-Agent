def __init__(self):
    self.ocr = None
    if PADDLE_AVAILABLE:
        try:
            self.ocr = PaddleOCR(
                lang='ch',
                use_angle_cls=True
            )
            print("PaddleOCR initialized successfully")
        except Exception as e:
            print(f"PaddleOCR initialization failed: {e}")
            self.ocr = None
    else:
        print("PaddleOCR not available, using mock mode")