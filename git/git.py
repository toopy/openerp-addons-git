from osv import osv
from osv import fields


class git_repositories(osv.osv):

    _name = 'git.repositories'
    _description = 'Git repositories.'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),
        'url': fields.char('URL', size=128, required=True, select=True)
    }

    def create(self, cr, uid, values, context=None):
        return super(git_repositories, self).create(cr, uid, values,
                                               context=context)

    def write(self, cr, uid, ids, values, context=None):
        return super(git_repositories, self).write(cr, uid, ids, values,
                                              context=context)


git_repositories()
