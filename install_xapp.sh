helm upgrade --install \
	--namespace riab \
	--values ./helm-charts/mobiflow-auditor/values.yaml \
	mobiflow-auditor \
	./helm-charts/mobiflow-auditor/ && \
	sleep 20 && \
	kubectl wait pod -n riab --for=condition=Ready -l app=mobiflow-auditor --timeout=600s
