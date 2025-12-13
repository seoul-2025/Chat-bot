#!/usr/bin/env python3
"""
DynamoDB 대화 데이터 마이그레이션 스크립트
복합 키 구조에서 단일 키 구조로 변경
"""
import boto3
import json
import time
from decimal import Decimal

def decimal_default(obj):
    """JSON 직렬화를 위한 Decimal 변환"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def migrate_conversations():
    """기존 테이블에서 새 테이블로 대화 데이터 마이그레이션"""
    
    # DynamoDB 클라이언트 설정
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    source_table = dynamodb.Table('nx-wt-prf-conversations')
    target_table = dynamodb.Table('nx-wt-prf-conversations-v2')
    
    print("🔄 데이터 마이그레이션 시작...")
    
    # 기존 테이블에서 모든 데이터 스캔
    response = source_table.scan()
    items = response['Items']
    
    # 페이지네이션 처리
    while 'LastEvaluatedKey' in response:
        response = source_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])
    
    print(f"📊 총 {len(items)}개 아이템 발견")
    
    # 배치 쓰기를 위한 설정
    success_count = 0
    error_count = 0
    batch_size = 25  # DynamoDB batch_writer 최대값
    
    # 배치 단위로 처리
    for i in range(0, len(items), batch_size):
        batch_items = items[i:i + batch_size]
        
        try:
            with target_table.batch_writer() as batch:
                for item in batch_items:
                    # 데이터 구조는 동일하게 유지 (키 구조만 변경됨)
                    batch.put_item(Item=item)
                    success_count += 1
            
            print(f"✅ 배치 {i//batch_size + 1}: {len(batch_items)}개 아이템 마이그레이션 완료")
            
            # API 레이트 리밋을 위한 잠시 대기
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ 배치 {i//batch_size + 1} 오류: {str(e)}")
            error_count += len(batch_items)
    
    print(f"\n🎉 마이그레이션 완료!")
    print(f"  ✅ 성공: {success_count}개")
    print(f"  ❌ 실패: {error_count}개")
    
    # 새 테이블 아이템 수 확인
    target_response = target_table.scan(Select='COUNT')
    target_count = target_response['Count']
    print(f"  📊 새 테이블 아이템 수: {target_count}개")
    
    return success_count, error_count

if __name__ == "__main__":
    try:
        success, error = migrate_conversations()
        if error == 0:
            print("\n✅ 모든 데이터가 성공적으로 마이그레이션되었습니다!")
        else:
            print(f"\n⚠️  일부 데이터 마이그레이션에 실패했습니다. 확인이 필요합니다.")
    except Exception as e:
        print(f"\n💥 마이그레이션 중 오류 발생: {str(e)}")