class Badge:
    def __init__(self,name,img) -> None:
        self.name = name
        self.img = img
        self.docs_uri = f'https://docs.vitznode.repl.co/badges/'

badges = {'Gründer':Badge('Gründer','/cdn/badge/founder.png'),'Website-Moderator':Badge('Website-Moderator','/cdn/badge/mod.png'),'Verifizierter Benutzer der ersten Stunde':Badge('Verifizierter Benutzer der ersten Stunde','/cdn/badge/certified-staff.png'),'Bughunter':Badge('Bughunter','/cdn/badge/bugbuster.png'),'Developer':Badge('Developer','/cdn/badge/developer.png')}

class Course:
    def __init__(self,name,endpoint):
        ...

def generate_badge(name):
    return badges[name]

random_names = [
    'electro','pancake','spoil','nuts','pancakeeater','muncher'
]