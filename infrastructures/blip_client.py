from transformers import BlipProcessor, BlipForConditionalGeneration

# グローバル変数でモデルとプロセッサーを保持
processor = None
model = None

def initialize_blip_model():
    """BLIPモデルとプロセッサーを初期化"""
    global processor, model

    if processor is None or model is None:
        print("BLIPモデルを初期化中...")
        model_name = "Salesforce/blip-image-captioning-large"
        
        # 警告を抑制してプロセッサー初期化
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Using a slow image processor")
            processor = BlipProcessor.from_pretrained(model_name, use_fast=True)
        model = BlipForConditionalGeneration.from_pretrained(model_name)

        print("BLIPモデルの初期化が完了しました")

def get_blip_model():
    """BLIPモデルとプロセッサーを取得"""
    return processor, model
