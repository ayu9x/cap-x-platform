"""
CI/CD Service
Manages continuous integration and deployment pipelines
"""

import logging
import subprocess
import json
from typing import Dict, List, Optional
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class CICDService:
    """Service for managing CI/CD pipeline operations"""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize CI/CD service
        
        Args:
            github_token: GitHub personal access token
        """
        self.github_token = github_token
        self.github_api_base = 'https://api.github.com'
    
    def _github_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make authenticated GitHub API request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request payload
            
        Returns:
            API response
        """
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f'{self.github_api_base}/{endpoint}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return {'success': False, 'error': f'Unsupported method: {method}'}
            
            response.raise_for_status()
            
            return {
                'success': True,
                'data': response.json() if response.content else {},
                'status_code': response.status_code
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None)
            }
    
    def trigger_workflow(self, owner: str, repo: str, workflow_id: str, 
                        ref: str = 'main', inputs: Optional[Dict] = None) -> Dict:
        """
        Trigger GitHub Actions workflow
        
        Args:
            owner: Repository owner
            repo: Repository name
            workflow_id: Workflow ID or filename
            ref: Git reference (branch, tag, SHA)
            inputs: Workflow inputs
            
        Returns:
            Trigger result
        """
        endpoint = f'repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches'
        
        data = {
            'ref': ref,
            'inputs': inputs or {}
        }
        
        result = self._github_request('POST', endpoint, data)
        
        if result['success']:
            return {
                'success': True,
                'workflow': workflow_id,
                'ref': ref,
                'message': 'Workflow triggered successfully'
            }
        
        return result
    
    def get_workflow_runs(self, owner: str, repo: str, workflow_id: Optional[str] = None,
                         status: Optional[str] = None, per_page: int = 30) -> Dict:
        """
        Get workflow runs
        
        Args:
            owner: Repository owner
            repo: Repository name
            workflow_id: Filter by workflow ID
            status: Filter by status (queued, in_progress, completed)
            per_page: Results per page
            
        Returns:
            Workflow runs
        """
        if workflow_id:
            endpoint = f'repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs'
        else:
            endpoint = f'repos/{owner}/{repo}/actions/runs'
        
        params = {'per_page': per_page}
        if status:
            params['status'] = status
        
        endpoint += '?' + '&'.join([f'{k}={v}' for k, v in params.items()])
        
        result = self._github_request('GET', endpoint)
        
        if result['success']:
            runs = result['data'].get('workflow_runs', [])
            return {
                'success': True,
                'count': len(runs),
                'runs': [
                    {
                        'id': run['id'],
                        'name': run['name'],
                        'status': run['status'],
                        'conclusion': run.get('conclusion'),
                        'created_at': run['created_at'],
                        'updated_at': run['updated_at'],
                        'head_branch': run['head_branch'],
                        'head_sha': run['head_sha']
                    }
                    for run in runs
                ]
            }
        
        return result
    
    def get_workflow_run_logs(self, owner: str, repo: str, run_id: int) -> Dict:
        """
        Get workflow run logs
        
        Args:
            owner: Repository owner
            repo: Repository name
            run_id: Workflow run ID
            
        Returns:
            Workflow logs
        """
        endpoint = f'repos/{owner}/{repo}/actions/runs/{run_id}/logs'
        
        result = self._github_request('GET', endpoint)
        
        return result
    
    def cancel_workflow_run(self, owner: str, repo: str, run_id: int) -> Dict:
        """
        Cancel a workflow run
        
        Args:
            owner: Repository owner
            repo: Repository name
            run_id: Workflow run ID
            
        Returns:
            Cancellation result
        """
        endpoint = f'repos/{owner}/{repo}/actions/runs/{run_id}/cancel'
        
        result = self._github_request('POST', endpoint)
        
        if result['success']:
            return {
                'success': True,
                'run_id': run_id,
                'message': 'Workflow run cancelled'
            }
        
        return result
    
    def build_docker_image(self, dockerfile_path: str, image_name: str, 
                          tag: str = 'latest', build_args: Optional[Dict] = None) -> Dict:
        """
        Build Docker image
        
        Args:
            dockerfile_path: Path to Dockerfile directory
            image_name: Image name
            tag: Image tag
            build_args: Build arguments
            
        Returns:
            Build result
        """
        try:
            command = ['docker', 'build', '-t', f'{image_name}:{tag}']
            
            if build_args:
                for key, value in build_args.items():
                    command.extend(['--build-arg', f'{key}={value}'])
            
            command.append(dockerfile_path)
            
            logger.info(f"Building Docker image: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            return {
                'success': result.returncode == 0,
                'image': f'{image_name}:{tag}',
                'output': result.stdout,
                'error': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Docker build timed out after 10 minutes'
            }
        except Exception as e:
            logger.error(f"Docker build failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def push_docker_image(self, image_name: str, tag: str = 'latest', 
                         registry: Optional[str] = None) -> Dict:
        """
        Push Docker image to registry
        
        Args:
            image_name: Image name
            tag: Image tag
            registry: Registry URL
            
        Returns:
            Push result
        """
        try:
            if registry:
                full_image = f'{registry}/{image_name}:{tag}'
                # Tag image for registry
                tag_result = subprocess.run(
                    ['docker', 'tag', f'{image_name}:{tag}', full_image],
                    capture_output=True,
                    text=True
                )
                if tag_result.returncode != 0:
                    return {
                        'success': False,
                        'error': f'Failed to tag image: {tag_result.stderr}'
                    }
            else:
                full_image = f'{image_name}:{tag}'
            
            logger.info(f"Pushing Docker image: {full_image}")
            
            result = subprocess.run(
                ['docker', 'push', full_image],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            return {
                'success': result.returncode == 0,
                'image': full_image,
                'output': result.stdout,
                'error': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Docker push timed out after 10 minutes'
            }
        except Exception as e:
            logger.error(f"Docker push failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_tests(self, test_command: str, working_dir: str = '.') -> Dict:
        """
        Run test suite
        
        Args:
            test_command: Test command to execute
            working_dir: Working directory
            
        Returns:
            Test results
        """
        try:
            logger.info(f"Running tests: {test_command}")
            
            result = subprocess.run(
                test_command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Tests timed out after 5 minutes'
            }
        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_pipeline(self, pipeline_config: Dict) -> Dict:
        """
        Create a CI/CD pipeline
        
        Args:
            pipeline_config: Pipeline configuration
            
        Returns:
            Pipeline creation result
        """
        try:
            pipeline_id = pipeline_config.get('id') or f"pipeline-{datetime.utcnow().timestamp()}"
            
            stages = []
            for stage in pipeline_config.get('stages', []):
                stage_result = {
                    'name': stage['name'],
                    'status': 'pending',
                    'started_at': None,
                    'completed_at': None
                }
                stages.append(stage_result)
            
            pipeline = {
                'id': pipeline_id,
                'name': pipeline_config.get('name', 'Unnamed Pipeline'),
                'repository': pipeline_config.get('repository'),
                'branch': pipeline_config.get('branch', 'main'),
                'status': 'created',
                'stages': stages,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            return {
                'success': True,
                'pipeline': pipeline
            }
        except Exception as e:
            logger.error(f"Pipeline creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_pipeline_stage(self, stage_config: Dict) -> Dict:
        """
        Execute a pipeline stage
        
        Args:
            stage_config: Stage configuration
            
        Returns:
            Stage execution result
        """
        try:
            stage_type = stage_config.get('type')
            
            if stage_type == 'build':
                return self.build_docker_image(
                    dockerfile_path=stage_config.get('dockerfile_path', '.'),
                    image_name=stage_config.get('image_name'),
                    tag=stage_config.get('tag', 'latest')
                )
            elif stage_type == 'test':
                return self.run_tests(
                    test_command=stage_config.get('command'),
                    working_dir=stage_config.get('working_dir', '.')
                )
            elif stage_type == 'deploy':
                # This would integrate with KubernetesService
                return {
                    'success': True,
                    'message': 'Deploy stage would be handled by KubernetesService'
                }
            else:
                return {
                    'success': False,
                    'error': f'Unknown stage type: {stage_type}'
                }
        except Exception as e:
            logger.error(f"Stage execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }