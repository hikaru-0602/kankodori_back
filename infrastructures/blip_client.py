from transformers import BlipProcessor, BlipForConditionalGeneration

# グローバル変数でモデルとプロセッサーを保持
processor = None
model = None

def initialize_blip_model():
    """BLIPモデルとプロセッサーを初期化"""
    global processor, model

    if processor is None or model is None:
        # 事前初期化済みモデルがあれば使用
        import os
        if os.path.exists('/app/models/blip_initialized.pth'):
            print("事前初期化済みBLIPモデルを読み込み中...")
            import torch
            saved_data = torch.load('/app/models/blip_initialized.pth', map_location='cpu', weights_only=False)
            processor = saved_data['processor']
            model = saved_data['model']
            print("事前初期化済みBLIPモデルの読み込み完了")
        else:
            # 従来通りダウンロード
            print("BLIPモデルをダウンロード中...")
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
