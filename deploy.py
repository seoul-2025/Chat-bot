import boto3
import json
import zipfile
import os
from pathlib import Path

def create_lambda_package():
    """Lambda 패키지 생성"""
    
    # 패키지 디렉토리 생성
    package_dir = Path("lambda_package")
    package_dir.mkdir(exist_ok=True)
    
    # 핸들러 파일들 복사
    import shutil
    shutil.copytree("backend", package_dir / "backend", dirs_exist_ok=True)
    
    # ZIP 파일 생성
    with zipfile.ZipFile("lambda_function.zip", "w") as zip_file:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, package_dir)
                zip_file.write(file_path, arc_name)
    
    # 임시 디렉토리 삭제
    shutil.rmtree(package_dir)
    
    return "lambda_function.zip"

def deploy_lambda_functions():
    """Lambda 함수들 배포"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # ZIP 패키지 생성
    zip_file = create_lambda_package()
    
    with open(zip_file, 'rb') as f:
        zip_content = f.read()
    
    functions = [
        {
            'name': 'one-websocket-connect',
            'handler': 'backend.handlers.websocket.connect_handler.lambda_handler'
        },
        {
            'name': 'one-websocket-disconnect', 
            'handler': 'backend.handlers.websocket.disconnect_handler.lambda_handler'
        },
        {
            'name': 'one-websocket-message',
            'handler': 'backend.handlers.websocket.message_handler.lambda_handler'
        },
        {
            'name': 'one-conversation-api',
            'handler': 'backend.handlers.api.conversation_handler.lambda_handler'
        },
        {
            'name': 'one-usage-handler',
            'handler': 'backend.handlers.api.usage_handler.lambda_handler'
        }
    ]
    
    for func in functions:
        try:
            # 함수 업데이트 시도
            lambda_client.update_function_code(
                FunctionName=func['name'],
                ZipFile=zip_content
            )
            print(f"✅ {func['name']} 업데이트 완료")
            
        except lambda_client.exceptions.ResourceNotFoundException:
            # 함수가 없으면 생성
            lambda_client.create_function(
                FunctionName=func['name'],
                Runtime='python3.9',
                Role='arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role',
                Handler=func['handler'],
                Code={'ZipFile': zip_content},
                Environment={
                    'Variables': {
                        'CLAUDE_API_KEY': os.environ.get('CLAUDE_API_KEY', '')
                    }
                }
            )
            print(f"✅ {func['name']} 생성 완료")
            
        except Exception as e:
            print(f"❌ {func['name']} 오류: {e}")
    
    # ZIP 파일 삭제
    os.remove(zip_file)

if __name__ == "__main__":
    deploy_lambda_functions()