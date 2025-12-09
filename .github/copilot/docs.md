# Documentation References

## Helm Documentation
- [Helm Documentation](https://helm.sh/docs/)
- [Helm Chart Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Helm Chart Template Guide](https://helm.sh/docs/chart_template_guide/)

## Kubernetes Documentation
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

## Nginx Documentation
- [Nginx Official Documentation](https://nginx.org/en/docs/)
- [Nginx Docker Hub](https://hub.docker.com/_/nginx)

## Project-Specific Documentation
- [README.md](./README.md) - Main project documentation
- [values.yaml](./values.yaml) - Default configuration values
- [Chart.yaml](./Chart.yaml) - Chart metadata

## Useful Commands Referencesh
# Install chart
helm install <release-name> . --namespace <namespace>

# Upgrade chart
helm upgrade <release-name> . --namespace <namespace>

# Uninstall chart
helm uninstall <release-name> --namespace <namespace>

# List releases
helm list --namespace <namespace>

# Get values
helm get values <release-name> --namespace <namespace>

# Template rendering (dry-run)
helm template <release-name> . --namespace <namespace>
