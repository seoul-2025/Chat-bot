// API 엔드포인트는 환경변수로 관리
const API_ENDPOINT = import.meta.env.VITE_API_BASE_URL || 'https://pinjzwk0qi.execute-api.us-east-1.amazonaws.com/prod';

// Cognito 인증 토큰 가져오기
const getAuthToken = async () => {
  try {
    // AWS Amplify나 Cognito SDK를 사용하여 토큰 가져오기
    // 현재는 임시로 null 반환 (인증 없이 시도)
    return null;
  } catch (error) {
    console.error('인증 토큰 가져오기 실패:', error);
    return null;
  }
};

// 프롬프트 조회 (설명, 지침, 파일 목록)
export const getPrompt = async (engineType) => {
  try {
    console.log('🔍 프롬프트 조회 시도:', `${API_ENDPOINT}/prompts/${engineType}`);
    
    const response = await fetch(`${API_ENDPOINT}/prompts/${engineType}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log('📡 응답 상태:', response.status, response.statusText);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('✅ 프롬프트 데이터 수신 성공');
    return data;
  } catch (error) {
    console.error('❌ 프롬프트 조회 실패:', error);
    
    // Fallback: 기본 프롬프트 데이터 반환
    console.log('🔧 Fallback: 기본 프롬프트 데이터 사용');
    const fallbackData = {
      engineType,
      description: engineType === '11' ? '기업 보도자료 분석 전문 AI' : '정부/공공기관 보도자료 분석 전문 AI',
      instructions: engineType === '11' 
        ? '기업 보도자료를 분석하여 맞춤형 기사를 작성해드립니다. 파일을 업로드하거나 텍스트를 입력해주세요.'
        : '정부/공공기관 보도자료를 분석하여 맞춤형 기사를 작성해드립니다. 파일을 업로드하거나 텍스트를 입력해주세요.',
      files: []
    };
    
    return fallbackData;
  }
};

// 프롬프트 업데이트 (설명, 지침만)
export const updatePrompt = async (engineType, updates) => {
  try {
    const response = await fetch(`${API_ENDPOINT}/prompts/${engineType}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error updating prompt:', error);
    throw error;
  }
};

// 파일 목록 조회
export const getFiles = async (engineType) => {
  // 개발 환경에서는 빈 배열 반환
  if (import.meta.env.DEV || !API_ENDPOINT) {
    console.log('🔧 개발 모드: 빈 파일 목록 반환');
    return [];
  }

  try {
    const response = await fetch(`${API_ENDPOINT}/prompts/${engineType}/files`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.files || [];
  } catch (error) {
    console.error('Error fetching files:', error);
    return [];
  }
};

// 파일 추가
export const addFile = async (engineType, file) => {
  const url = `${API_ENDPOINT}/prompts/${engineType}/files`;
  console.log('Adding file to:', url);
  console.log('Request body:', { fileName: file.fileName, fileContent: file.fileContent });
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        fileName: file.fileName,
        fileContent: file.fileContent,
      }),
    });

    console.log('Response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Response error:', errorText);
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    const data = await response.json();
    console.log('Response data:', data);
    return data.file;
  } catch (error) {
    console.error('Error adding file:', error);
    console.error('Error details:', {
      message: error.message,
      stack: error.stack,
      url: url
    });
    throw error;
  }
};

// 파일 수정
export const updateFile = async (engineType, fileId, updates) => {
  try {
    const response = await fetch(`${API_ENDPOINT}/prompts/${engineType}/files/${fileId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error updating file:', error);
    throw error;
  }
};

// 파일 삭제
export const deleteFile = async (engineType, fileId) => {
  try {
    const response = await fetch(`${API_ENDPOINT}/prompts/${engineType}/files/${fileId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error deleting file:', error);
    throw error;
  }
};