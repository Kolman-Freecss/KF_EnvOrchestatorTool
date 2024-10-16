output "jenkins_public_ip" {
  description = "Public IP address of the Jenkins instance"
  value       = aws_instance.jenkins_server.public_ip
}

output "jenkins_url" {
  description = "URL of the Jenkins instance"
  value       = "http://${aws_instance.jenkins_server.public_ip}:8080"
}
