# 專案建置流程
1. 到Certificate Manager 中去request你的網域(假設我的網域是yueyue.site，以下作{你的網域})，加入`{你的網域}`和`*.{你的網域}`，並提出申請
2. 給我申請的CNAME_name 和 CNAME_value
3. 執行network-stack
4. 執行security-stack
5. 執行data-sta
6. 去Certificate Manager將剛剛申請的SSL憑證的ARN複製起來 (會有一串類似arn:aws:acm:us-east-1:....)
7. 找到app-stack.yml中的，並將其中的Default replace成你剛剛複製的內容
```
CertificateArn:
    Type: String
    Default: arn:aws:acm:us-east-1:534207971056:certificate/a93ab9b7-1021-45ff-8c5e-89f162d803c2
    Description: "The ARN of the SSL certificate in AWS ACM"
```
8. 將app-stack.yml 中的ec2 userdata中的COGNITO_REDIRECT_URL的值改成你的網域
9. 執行app-stack
10. 去將load balancer的DNS_name給我
