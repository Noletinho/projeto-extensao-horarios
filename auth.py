from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash


def usuario_logado():
    if 'usuario_id' not in session:
        return None
    return {
        'id': session['usuario_id'],
        'nome': session['usuario_nome'],
        'perfil': session['usuario_perfil'],
        'id_professor': session.get('usuario_id_professor'),
        'primeiro_login': session.get('usuario_primeiro_login', 0),
    }


def requer_login(f):
    @wraps(f)
    def decorado(*args, **kwargs):
        if not usuario_logado():
            flash("Faça login para continuar.", 'erro')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorado


def requer_perfil(*perfis):
    def decorador(f):
        @wraps(f)
        def decorado(*args, **kwargs):
            u = usuario_logado()
            if not u:
                flash("Faça login para continuar.", 'erro')
                return redirect(url_for('login'))
            if u['perfil'] not in perfis:
                flash("Você não tem permissão para acessar esta página.", 'erro')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorado
    return decorador
