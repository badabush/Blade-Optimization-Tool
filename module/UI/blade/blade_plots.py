import numpy as np

from module.blade.bladegen import BladeGen

def bladePlot(ax, ds, ds1=0, ds2=0, ds_import=0,xlim=(0,0),ylim=(0,0)):
    """
    Main window plot widget content. Differentiates between single/tandem, seperate control of tandem blades.

    :param ds: Data from single blade
    :type ds: pandas.DataFrame
    :param ds1: Data from 1st tandem blade, 0 if not specified
    :type ds1: pandas.DataFrame
    :param ds2: Data from 2nd tandem blade, 0 if not specified
    :type ds2: pandas.DataFrame
    :param ds_import: Data from imported blade, 0 if not specified
    :type ds_import: pandas.DataFrame
    :return: None
    """
    # get zoom state
    if xlim == (0, 0) and ylim == (0, 0):
        xlim = (-.1, 1)
        ylim = (-.1, 1)
    else:
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
    ax.cla()  # clear existing plots

    """
    Update Single Blade/Both blades at once with the same parameters
    """

    if ds['nblades'] == 'single':
        """Single blade"""
        bladegen = BladeGen(frontend='UI', nblade=ds['nblades'], th_dist_option=ds['thdist_ver'], npts=ds['npts'],
                            alpha1=ds['alpha1'], alpha2=ds['alpha2'],
                            lambd=ds['lambd'], th=ds['th'], x_maxth=ds['xmax_th'], x_maxcamber=ds['xmax_camber'],
                            l_chord=ds['l_chord'], th_le=ds['th_le'], th_te=ds['th_te'], spline_pts=ds['pts'],
                            thdist_points=ds['pts_th'])
        blade_data, camber_data = bladegen._return()
        division = ds['dist_blades'] * ds['l_chord']
        ax.plot(blade_data[:, 0], blade_data[:, 1], color='royalblue')
        ax.fill(blade_data[:, 0], blade_data[:, 1], color='cornflowerblue', alpha=.5)
        ax.plot(blade_data[:, 0], blade_data[:, 1] + division, color='royalblue')
        ax.fill(blade_data[:, 0], blade_data[:, 1] + division, color='cornflowerblue', alpha=.5)

        ax.plot(camber_data[::15, 0], camber_data[::15, 1], linestyle='--', dashes=(5, 5), color='darkblue')
        ax.plot(camber_data[::15, 0], camber_data[::15, 1] + division, linestyle='--', dashes=(5, 5),
                     color='darkblue', alpha=.7)
        plt_df = {'type': 'single', 'blade': blade_data, 'camber': camber_data}

    elif ds['nblades'] == 'tandem':
        """Tandem blades"""
        df_blades = {}
        # Update either both blades at once or blades seperately.
        dataselect = [ds1, ds2]
        for i in [0, 1]:
            df = dataselect[i]
            bladegen = BladeGen(frontend='UI', nblade=df['nblades'], th_dist_option=df['thdist_ver'],
                                npts=df['npts'],
                                alpha1=df['alpha1'], alpha2=df['alpha2'],
                                lambd=df['lambd'], th=df['th'], x_maxth=df['xmax_th'],
                                x_maxcamber=df['xmax_camber'],
                                l_chord=df['l_chord'], th_le=df['th_le'], th_te=df['th_te'], spline_pts=df['pts'],
                                thdist_points=df['pts_th'])
            blade_data, camber_data = bladegen._return()
            division = df['dist_blades'] * df['l_chord']
            # Update simultaneously
            blade1 = blade_data
            blade2 = np.copy(blade1)
            camber1 = camber_data
            camber2 = np.copy(camber_data)

            # save blades with _index for selective updating plot
            df_blades['blade1_%i' % (i + 1)] = blade1
            df_blades['blade2_%i' % (i + 1)] = blade2
            df_blades['camber1_%i' % (i + 1)] = camber1
            df_blades['camber2_%i' % (i + 1)] = camber2

        if ds['selected_blade'] == 0:
            """Update both blades at once"""
            blade2[:, 0] = blade2[:, 0] + blade1[0, 0]
            blade2[:, 1] = blade2[:, 1] + blade1[0, 1]
            camber2[:, 0] = camber2[:, 0] + blade1[0, 0]
            camber2[:, 1] = camber2[:, 1] + blade1[0, 1]
            # tandem blade 1 (lower)
            ax.plot(blade1[:, 0], blade1[:, 1], color='royalblue')
            ax.fill(blade1[:, 0], blade1[:, 1], color='cornflowerblue', alpha=.5)
            ax.plot(camber1[::15, 0], camber1[::15, 1], linestyle='--', dashes=(5, 5), color='darkblue',
                         alpha=.7)
            # tandem blade 2 (lower)
            ax.plot(blade2[:, 0] + ds1['x_offset'], blade2[:, 1] + ds1['y_offset'], color='indianred')
            ax.fill(blade2[:, 0] + ds1['x_offset'], blade2[:, 1] + ds1['y_offset'], color='lightcoral',
                         alpha=.5)
            ax.plot(camber2[::15, 0] + ds1['x_offset'], camber2[::15, 1] + ds1['y_offset'], linestyle='--',
                         dashes=(5, 5), color='darkred',
                         alpha=.7)
            # tandem blade 1 (upper)
            ax.plot(blade1[:, 0], blade1[:, 1] + division, color='royalblue')
            ax.fill(blade1[:, 0], blade1[:, 1] + division, color='cornflowerblue', alpha=.5)
            ax.plot(camber1[::15, 0], camber1[::15, 1] + division, linestyle='--', dashes=(5, 5),
                         color='darkblue', alpha=.7)
            # tandem blade 2 (upper)
            ax.plot(blade2[:, 0] + ds1['x_offset'], blade2[:, 1] + division + ds1['y_offset'],
                         color='indianred')
            ax.fill(blade2[:, 0] + ds1['x_offset'], blade2[:, 1] + division + ds1['y_offset'],
                         color='lightcoral', alpha=.5)
            ax.plot(camber2[::15, 0] + ds1['x_offset'], camber2[::15, 1] + division + ds1['y_offset'],
                         linestyle='--', dashes=(5, 5),
                         color='darkred', alpha=.7)

        else:
            """ Update blades seperately """
            # # calculate where nose of tandem 2 starts
            df_blades['blade2_2'][:, 0] = df_blades['blade2_2'][:, 0] + df_blades['blade1_1'][0, 0]
            df_blades['blade2_2'][:, 1] = df_blades['blade2_2'][:, 1] + df_blades['blade1_1'][0, 1]
            df_blades['camber2_2'][:, 0] = df_blades['camber2_2'][:, 0] + df_blades['blade1_1'][0, 0]
            df_blades['camber2_2'][:, 1] = df_blades['camber2_2'][:, 1] + df_blades['blade1_1'][0, 1]
            ax.plot(df_blades['blade1_1'][:, 0], df_blades['blade1_1'][:, 1], color='royalblue')
            ax.fill(df_blades['blade1_1'][:, 0], df_blades['blade1_1'][:, 1], color='cornflowerblue', alpha=.5)
            ax.plot(df_blades['camber1_1'][::15, 0], df_blades['camber1_1'][::15, 1], linestyle='--',
                         dashes=(5, 5), color='darkblue', alpha=.7)
            ax.plot(df_blades['blade2_2'][:, 0] + ds2['x_offset'],
                         df_blades['blade2_2'][:, 1] - ds2['y_offset'], color='indianred')
            ax.fill(df_blades['blade2_2'][:, 0] + ds2['x_offset'],
                         df_blades['blade2_2'][:, 1] - ds2['y_offset'], color='lightcoral', alpha=.5)
            ax.plot(df_blades['camber2_2'][::15, 0] + ds2['x_offset'],
                         df_blades['camber2_2'][::15, 1] - ds2['y_offset'], linestyle='--',
                         dashes=(5, 5), color='darkred', alpha=.7)

            ax.plot(df_blades['blade1_1'][:, 0], df_blades['blade1_1'][:, 1] + division, color='royalblue')
            ax.fill(df_blades['blade1_1'][:, 0], df_blades['blade1_1'][:, 1] + division,
                         color='cornflowerblue', alpha=.5)
            ax.plot(df_blades['camber1_1'][::15, 0], df_blades['camber1_1'][::15, 1] + division,
                         linestyle='--', dashes=(5, 5), color='darkblue', alpha=.7)
            ax.plot(df_blades['blade2_2'][:, 0] + ds2['x_offset'],
                         df_blades['blade2_2'][:, 1] + division - ds2['y_offset'], color='indianred')
            ax.fill(df_blades['blade2_2'][:, 0] + ds2['x_offset'],
                         df_blades['blade2_2'][:, 1] + division - ds2['y_offset'], color='lightcoral',
                         alpha=.5)
            ax.plot(df_blades['camber2_2'][::15, 0] + ds2['x_offset'],
                         df_blades['camber2_2'][::15, 1] + division - ds2['y_offset'],
                         linestyle='--', dashes=(5, 5), color='darkred', alpha=.7)

            df_blades['type'] = 'tandem'
            plt_df = df_blades

    """ Plot imported blade if exists """
    try:
        if ds['nblades'] == 'single':
            ax.plot(ds_import.x + ds_import.x_offset, ds_import.y + ds_import.y_offset, 'r')
        else:
            # get position of second blade
            blade_import1 = np.array([ds_import.x1, ds_import.y1]).T
            blade_import2 = np.array([ds_import.x2, ds_import.y2]).T

            blade_import2[:, 0] = blade_import2[:, 0] + blade_import1[0, 0]
            blade_import2[:, 1] = blade_import2[:, 1] + blade_import1[0, 1]

            ax.plot(blade_import1[:, 0] + ds_import.x_offset,
                         blade_import1[:, 1] + ds_import.y_offset, 'r')
            ax.plot(blade_import2[:, 0] + ds_import.x_offset + ds2['x_offset'],
                         blade_import2[:, 1] + ds_import.y_offset - ds2['y_offset'], 'r')
    except AttributeError:
        # print("Error plotting imported blade.")
        pass
    ax.axis('equal')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.grid()