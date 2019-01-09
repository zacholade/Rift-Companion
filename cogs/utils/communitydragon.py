import re

BASE_URL = "https://cdn.communitydragon.org/{patch}"

# Information on this can be found @
# https://www.communitydragon.org/docs


class CommunityDragon(object):

    @staticmethod
    def gen_url(url, **kwargs):
        url = BASE_URL + url
        url_params = re.findall(r"{(\w*)}", url)

        if "" in url_params:
            raise ValueError("nameless format parameters not supported!")

        for req_param in url_params:
            if req_param not in kwargs:
                raise ValueError(f'parameter "{req_param}" is required!')

        return url.format(**kwargs)

    @staticmethod
    def square_icon(champion_id, patch='latest'):
        """
        Returns the default small square icon url of a champion
        which is found during champion select.
        """
        return CommunityDragon.gen_url('/champion/{champion_id}/square', champion_id=champion_id, patch=patch)

    @staticmethod
    def data(champion_id, patch='latest'):
        """
        Returns the url which can be used to get all information
        on a specific champion.
        """
        return CommunityDragon.gen_url('/champion/{champion_id}/data', champion_id=champion_id, patch=patch)

    @staticmethod
    def splash_art(champion_id, skin_id=None, centered=False, patch='latest'):
        """
        Returns the full 1920x1080 splash art of a champion.
        If skin_id, the splash of the skin will be shown instead.
        If centered, the splash art will be centered on the champion.
        """
        url = '/champion/{champion_id}/splash-art'
        url = url + '/centered' if centered else url
        url = url + '/skin/{skin_id}' if skin_id else url
        return CommunityDragon.gen_url(url, champion_id=champion_id, patch=patch, skin_id=skin_id)

    @staticmethod
    def tile(champion_id, skin_id=None, patch='latest'):
        """
        Returns a larger version of the square icon url which
        can be seen in champion select. Optional skin_id.
        """
        url = '/champion/{champion_id}/tile'
        url = url + '/skin/{skin_id}' if skin_id else url
        return CommunityDragon.gen_url(url, champion_id=champion_id, patch=patch, skin_id=skin_id)

    @staticmethod
    def portrait(champion_id, skin_id=None, patch='latest'):
        """
        Returns the loading portrait url of a chammpion which is
        seen during the loading screen
        """
        url = '/champion/{champion_id}/portrait'
        url = url + '/skin/{skin_id}' if skin_id else url
        return CommunityDragon.gen_url(url, champion_id=champion_id, patch=patch, skin_id=skin_id)

    @staticmethod
    def ability(champion_id, ability, patch='latest'):
        """
        Returns the icon url of an ability/passive.
        """
        if not isinstance(ability, str):
            raise ValueError('Ability must be of type str.')
        
        if ability.lower() not in ['q','w','e','r','passive']:
            raise ValueError('Ability must be either q, w, e, r or passive')

        url = '/champion/{champion_id}/ability-icon/{ability}'
        return CommunityDragon.gen_url(url, champion_id=champion_id, patch=patch, ability=ability)

    @staticmethod
    def ward_icon(ward_id, shadow=False, patch='latest'):
        """
        Returns the icon url of a ward.
        If shadow is True, the image will be just the shadow made by the ward.
        """
        url = '/ward/{ward_id}'
        url = url + '/shadow' if shadow else url
        return CommunityDragon.gen_url(url, ward_id=ward_id, patch=patch)

    @staticmethod
    def honor_placeholder(patch='latest'):
        """
        Returns the placeholder for the honor emblem
        """
        return CommunityDragon.gen_url('/honor/emblem/generic', patch=patch)

    @staticmethod
    def honor_emblem(honor_id, locked=False, checkpoint_id=None, patch='latest'):
        """
        Returns an honor embled url for a particular honor level.
        If checkpoint_id is provided, it will include the checkpoint level in the image.
        if locked is True; the emblem will have a lock over it.
        """
        url = '/honor/emblem/{honor_id}'
        if locked:
            return CommunityDragon.gen_url(url + '/locked', honor_id=honor_id, locked=locked, patch=patch)

        url = url + '/level/{checkpoint_id}' if checkpoint_id else url
        return CommunityDragon.gen_url(url, honor_id=honor_id, checkpoint_id=checkpoint_id, patch=patch)
