{{- define "kubernetes-server.image" -}}
{{ .Values.global.dockerRegistry }}{{ . }}
{{- end -}}