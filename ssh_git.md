  42 ls ~/.ssh
  46 mv C:\Users\Administrator\.ssh\ C:\Users\Administrator\.ssh2
  47 ssh-keygen
  一路回车
  48 ls ~/.ssh
  49 cat C:\Users\Administrator\.ssh\id_ed25519.pub

此处复制pub到github setting的ssh key中 保存后即可

  50 ssh -T git@github.com
  51 git remote set-url origin git@github.com:swujing822/ws.git
  52 git pull
  53 git push