# Kankodori Backend - Clean Architecture Structure

## 既存実装に基づくクリーンアーキテクチャ構造

### 既存の実装分析結果

既存のコードベースを分析し、実際に実装されている関数のみに限定した構造を以下に示します。

```
src/
├── domain/                          # 最内層 - ビジネスルール
│   ├── entities/
│   │   ├── tourist_spot.py          # 観光地エンティティ
│   │   ├── similarity_result.py     # 類似度結果エンティティ
│   │   ├── search_query.py          # 検索クエリエンティティ
│   │   └── content_vector.py        # ベクトルエンティティ
│   ├── value_objects/
│   │   ├── similarity_score.py      # 類似度スコア値オブジェクト
│   │   ├── search_range.py          # 検索範囲値オブジェクト
│   │   └── location_filter.py       # 地名フィルター値オブジェクト
│   └── repositories/                # リポジトリインターフェース（既存関数ベース）
│       ├── firebase_data_repository.py      # Firebase データアクセス
│       ├── vectorization_repository.py     # ベクトル化処理
│       └── content_generation_repository.py # コンテンツ生成
│
├── application/                     # アプリケーション層 - ユースケース
│   ├── use_cases/
│   │   ├── search_tourist_spots_use_case.py    # 観光地検索
│   │   ├── calculate_similarity_use_case.py    # 類似度計算
│   │   ├── generate_content_use_case.py        # コンテンツ生成
│   │   └── suggest_images_use_case.py          # 画像提案
│   └── services/                    # アプリケーションサービス
│       ├── similarity_integration_service.py  # 類似度統合
│       └── search_orchestration_service.py    # 検索オーケストレーション
│
├── infrastructure/                  # 最外層 - 既存implementationsベース
│   ├── repositories/                # リポジトリ実装
│   │   └── firebase_data_repository_impl.py
│   ├── vectorizers/                 # ベクトル化実装
│   │   ├── bert_vectorizer.py       # 既存: BertVectorizer
│   │   └── vit_vectorizer.py        # 既存: ViTVectorizer
│   ├── external_clients/            # 外部クライアント
│   │   ├── huggingface_client.py    # 既存: HuggingFaceImageClient
│   │   ├── blip_client.py           # 既存: BLIP関数
│   │   └── translation_client.py    # 既存: 翻訳機能
│   ├── processors/                  # プロセッサー
│   │   ├── image_processor.py       # 既存: ImageProcessor
│   │   └── file_manager.py          # 既存: FileManager
│   └── config/
│       └── firebase_config.py       # 既存: Firebase設定
│
└── interfaces/                      # インターフェース層
    └── controllers/
        └── search_controller.py     # 既存コントローラー
```

## 既存関数の再配置マッピング

### Domain Layer (ドメイン層) - 新規実装

```python
# domain/entities/tourist_spot.py
class TouristSpot:
    def calculate_weighted_similarity()  # ビジネスルール

# domain/value_objects/search_range.py
class SearchRange:
    def get_text_weight()               # 重み計算
    def get_image_weight()              # 重み計算
```

### Application Layer (アプリケーション層) - ユースケース再構成

```python
# application/use_cases/search_tourist_spots_use_case.py
execute()                             # search_tourist_spots()を移行

# application/use_cases/calculate_similarity_use_case.py
calculate_text_similarity()           # text_caluculate()を移行
calculate_image_similarity()          # image_caluculate()を移行
integrate_similarities()              # integrate_similarities()を移行

# application/use_cases/generate_content_use_case.py
generate_text_from_image()            # text_generate()を移行
generate_image_from_text()            # image_generate()を移行
create_enhanced_prompt()              # create_enhanced_prompt()を移行

# application/use_cases/suggest_images_use_case.py
get_random_suggestions()              # random_suggest()を移行
get_suggested_images()                # get_suggested_images()を移行
```

### Infrastructure Layer (インフラ層) - 既存実装維持

```python
# infrastructure/vectorizers/bert_vectorizer.py
text_vector()                         # 既存: services/bert.py

# infrastructure/vectorizers/vit_vectorizer.py
get_image_vector()                    # 既存: services/vit.py

# infrastructure/repositories/firebase_data_repository_impl.py
get_photo_data()                      # 既存: services/firebase_service.py
add_query_image()                     # 既存: services/firebase_service.py
get_feature()                         # 既存: services/firebase_service.py
get_api_query_images()               # 既存: services/firebase_service.py

# infrastructure/processors/ (既存のinfrastructures/を活用)
similarity_sort()                     # 既存: services/similarity_service.py
filter_location()                     # 既存: services/location_service.py
keyword()                             # 既存: services/mecab.py
```

### Domain Repository Interfaces (実際の関数に基づく)

```python
# domain/repositories/firebase_data_repository.py
class FirebaseDataRepository(ABC):
    async def get_photo_data() -> Optional[List[Any]]
    async def add_query_image(new_item: Dict[str, Any]) -> bool
    async def get_feature(filename: str) -> Optional[tuple[Dict[str, Any], List[str]]]
    async def get_api_query_images() -> List[str]

# domain/repositories/vectorization_repository.py
class VectorizationRepository(ABC):
    def text_vector(text: str) -> Optional[np.ndarray]
    def get_image_vector(image_data: bytes) -> Optional[np.ndarray]
    def similarity_sort(...) -> List[Dict[str, Any]]
    def filter_location(...) -> List[Dict[str, Any]]
    async def keyword(text: str) -> List[Dict[str, Any]]

# domain/repositories/content_generation_repository.py
class ContentGenerationRepository(ABC):
    async def text_generate(image: UploadFile) -> Optional[str]
    async def image_generate(prompt: str) -> Optional[Image.Image]
    def create_enhanced_prompt(user_input: str) -> str
```

## 依存関係の方向

```
Controllers → Use Cases → Domain Entities
     ↓            ↓            ↑
Repositories ← Infrastructure ←┘
```

## 利点

- **独立性**: ドメインロジックが外部依存から完全分離
- **テスタビリティ**: 各層を独立してテスト可能
- **変更容易性**: 外部技術変更の影響がドメインに及ばない
- **ビジネスルール中心**: ドメインエンティティにビジネスロジックを集約
- **依存性逆転**: 抽象に依存し、具象に依存しない
