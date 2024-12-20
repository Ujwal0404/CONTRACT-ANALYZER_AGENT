# app/api/routes/contracts.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from typing import List
from app.models.schemas import ContractAnalysisRequest, AnalysisReport
from app.core.analyzer import ContractAnalyzer
from app.api.dependencies import get_llm_service, get_storage_service
from app.config import get_settings
from app.utils import ValidationError, logger

router = APIRouter(prefix="/contracts", tags=["contracts"])

@router.post(
    "/analyze",
    response_model=AnalysisReport,
    summary="Analyze a single contract",
    description="Upload and analyze a contract file for compliance with specified regulations"
)
async def analyze_contract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    request: ContractAnalysisRequest = Depends(),
    settings = Depends(get_settings)
):
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith(tuple(settings.ALLOWED_EXTENSIONS)):
            raise ValidationError(f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}")
        
        async with get_storage_service(settings) as storage_service:
            # Save file temporarily
            temp_path = await storage_service.save_temp_file(file)
            background_tasks.add_task(storage_service.delete_temp_file, temp_path)

            async with get_llm_service(settings) as llm_service:
                # Analyze contract
                analyzer = ContractAnalyzer(llm_service)
                results = await analyzer.analyze_contract(temp_path, request.regulations)
                
                return results

    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/analyze-batch",
    response_model=List[AnalysisReport],
    summary="Analyze multiple contracts",
    description="Upload and analyze multiple contract files in batch"
)
async def analyze_multiple_contracts(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    request: ContractAnalysisRequest = Depends(),
    settings = Depends(get_settings)
):
    try:
        temp_paths = []
        async with get_storage_service(settings) as storage_service:
            for file in files:
                # Validate file type
                if not file.filename or not file.filename.lower().endswith(tuple(settings.ALLOWED_EXTENSIONS)):
                    raise ValidationError(f"Invalid file type: {file.filename}")
                
                # Save file temporarily
                temp_path = await storage_service.save_temp_file(file)
                temp_paths.append(temp_path)
                background_tasks.add_task(storage_service.delete_temp_file, temp_path)

            async with get_llm_service(settings) as llm_service:
                # Analyze contracts
                analyzer = ContractAnalyzer(llm_service)
                results = await analyzer.analyze_multiple_contracts(temp_paths, request.regulations)
                
                return results

    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))