"""
Terraform Service
Manages infrastructure as code using Terraform for AWS resources
"""

import os
import json
import logging
import subprocess
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TerraformService:
    """Service for managing Terraform infrastructure operations"""
    
    def __init__(self, working_dir: str = None):
        """
        Initialize Terraform service
        
        Args:
            working_dir: Directory containing Terraform configuration files
        """
        self.working_dir = working_dir or os.path.join(os.getcwd(), 'infrastructure', 'terraform')
        self.terraform_binary = self._find_terraform_binary()
        
    def _find_terraform_binary(self) -> str:
        """Find Terraform binary in system PATH"""
        try:
            result = subprocess.run(['which', 'terraform'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return 'terraform'  # Fallback to assuming it's in PATH
        except Exception:
            return 'terraform'
    
    def _run_command(self, command: List[str], capture_output: bool = True) -> Dict:
        """
        Execute Terraform command
        
        Args:
            command: Command and arguments to execute
            capture_output: Whether to capture output
            
        Returns:
            Dict with success status, output, and error
        """
        try:
            logger.info(f"Executing Terraform command: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                cwd=self.working_dir,
                capture_output=capture_output,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
        except subprocess.TimeoutExpired:
            logger.error("Terraform command timed out")
            return {
                'success': False,
                'output': '',
                'error': 'Command timed out after 5 minutes',
                'return_code': -1
            }
        except Exception as e:
            logger.error(f"Terraform command failed: {str(e)}")
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }
    
    def init(self, backend_config: Optional[Dict] = None) -> Dict:
        """
        Initialize Terraform working directory
        
        Args:
            backend_config: Backend configuration options
            
        Returns:
            Result of terraform init
        """
        command = [self.terraform_binary, 'init']
        
        if backend_config:
            for key, value in backend_config.items():
                command.extend([f'-backend-config={key}={value}'])
        
        return self._run_command(command)
    
    def plan(self, var_file: Optional[str] = None, variables: Optional[Dict] = None) -> Dict:
        """
        Create Terraform execution plan
        
        Args:
            var_file: Path to variables file
            variables: Dictionary of variables
            
        Returns:
            Result of terraform plan
        """
        command = [self.terraform_binary, 'plan', '-out=tfplan']
        
        if var_file:
            command.append(f'-var-file={var_file}')
        
        if variables:
            for key, value in variables.items():
                command.append(f'-var={key}={value}')
        
        return self._run_command(command)
    
    def apply(self, auto_approve: bool = False) -> Dict:
        """
        Apply Terraform changes
        
        Args:
            auto_approve: Skip interactive approval
            
        Returns:
            Result of terraform apply
        """
        command = [self.terraform_binary, 'apply']
        
        if auto_approve:
            command.append('-auto-approve')
        else:
            command.append('tfplan')
        
        return self._run_command(command)
    
    def destroy(self, auto_approve: bool = False, target: Optional[str] = None) -> Dict:
        """
        Destroy Terraform-managed infrastructure
        
        Args:
            auto_approve: Skip interactive approval
            target: Specific resource to destroy
            
        Returns:
            Result of terraform destroy
        """
        command = [self.terraform_binary, 'destroy']
        
        if auto_approve:
            command.append('-auto-approve')
        
        if target:
            command.append(f'-target={target}')
        
        return self._run_command(command)
    
    def output(self, output_name: Optional[str] = None) -> Dict:
        """
        Get Terraform outputs
        
        Args:
            output_name: Specific output to retrieve
            
        Returns:
            Terraform outputs as dictionary
        """
        command = [self.terraform_binary, 'output', '-json']
        
        if output_name:
            command.append(output_name)
        
        result = self._run_command(command)
        
        if result['success']:
            try:
                result['outputs'] = json.loads(result['output'])
            except json.JSONDecodeError:
                result['outputs'] = {}
        
        return result
    
    def validate(self) -> Dict:
        """
        Validate Terraform configuration
        
        Returns:
            Result of terraform validate
        """
        command = [self.terraform_binary, 'validate', '-json']
        result = self._run_command(command)
        
        if result['success']:
            try:
                result['validation'] = json.loads(result['output'])
            except json.JSONDecodeError:
                pass
        
        return result
    
    def state_list(self) -> Dict:
        """
        List resources in Terraform state
        
        Returns:
            List of resources
        """
        command = [self.terraform_binary, 'state', 'list']
        result = self._run_command(command)
        
        if result['success']:
            result['resources'] = [
                line.strip() for line in result['output'].split('\n') if line.strip()
            ]
        
        return result
    
    def import_resource(self, address: str, resource_id: str) -> Dict:
        """
        Import existing resource into Terraform state
        
        Args:
            address: Resource address in Terraform
            resource_id: Cloud provider resource ID
            
        Returns:
            Result of terraform import
        """
        command = [self.terraform_binary, 'import', address, resource_id]
        return self._run_command(command)
    
    def workspace_list(self) -> Dict:
        """
        List Terraform workspaces
        
        Returns:
            List of workspaces
        """
        command = [self.terraform_binary, 'workspace', 'list']
        result = self._run_command(command)
        
        if result['success']:
            workspaces = []
            for line in result['output'].split('\n'):
                line = line.strip()
                if line:
                    # Remove asterisk from current workspace
                    workspace = line.replace('*', '').strip()
                    workspaces.append(workspace)
            result['workspaces'] = workspaces
        
        return result
    
    def workspace_select(self, workspace: str) -> Dict:
        """
        Select Terraform workspace
        
        Args:
            workspace: Workspace name
            
        Returns:
            Result of workspace select
        """
        command = [self.terraform_binary, 'workspace', 'select', workspace]
        return self._run_command(command)
    
    def workspace_new(self, workspace: str) -> Dict:
        """
        Create new Terraform workspace
        
        Args:
            workspace: Workspace name
            
        Returns:
            Result of workspace new
        """
        command = [self.terraform_binary, 'workspace', 'new', workspace]
        return self._run_command(command)
    
    def provision_infrastructure(self, environment: str, config: Dict) -> Dict:
        """
        High-level method to provision infrastructure for an environment
        
        Args:
            environment: Environment name (dev, staging, prod)
            config: Configuration dictionary
            
        Returns:
            Provisioning result
        """
        try:
            # Initialize Terraform
            init_result = self.init()
            if not init_result['success']:
                return {
                    'success': False,
                    'error': 'Terraform initialization failed',
                    'details': init_result
                }
            
            # Select or create workspace
            workspace_result = self.workspace_select(environment)
            if not workspace_result['success']:
                workspace_result = self.workspace_new(environment)
                if not workspace_result['success']:
                    return {
                        'success': False,
                        'error': f'Failed to create workspace: {environment}',
                        'details': workspace_result
                    }
            
            # Validate configuration
            validate_result = self.validate()
            if not validate_result['success']:
                return {
                    'success': False,
                    'error': 'Terraform configuration validation failed',
                    'details': validate_result
                }
            
            # Create plan
            plan_result = self.plan(variables=config)
            if not plan_result['success']:
                return {
                    'success': False,
                    'error': 'Terraform plan failed',
                    'details': plan_result
                }
            
            # Apply changes
            apply_result = self.apply(auto_approve=False)
            
            return {
                'success': apply_result['success'],
                'environment': environment,
                'outputs': self.output() if apply_result['success'] else {},
                'details': apply_result
            }
            
        except Exception as e:
            logger.error(f"Infrastructure provisioning failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
