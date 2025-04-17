import logging
# import os
import traceback
# import subprocess as sbp

# import sgio.utils.logger as mul
import sgio.utils.execu as sue
# import msgpi.timer as mtime
# import msgd.builder.presg as msp
# import sgio.io as msi
# import msgpi.utils as utils
import sgio.utils as sutl
# import sgio._global as GLOBAL

logger = logging.getLogger(__name__)


def run(
    solver, input_name, analysis, smdim=2,
    aperiodic=False, output_gmsh_format=True, reduced_integration=False,
    scrnout=True, timeout=3600):
    """Run codes.

    Parameters
    ----------
    solver : str
        solver name of VABS or SwiftComp
    input_name : str
        Name of the input file.
    analysis : {0, 1, 2, 3, 4, 5, '', 'h', 'dn', 'dl', 'd', 'l', 'fi', 'f', 'fe'}
        Analysis to be carried out.

        * 0 or 'h' or '' - homogenization
        * 1 or 'dn' - (VABS) dehomogenization (nonlinear)
        * 2 or 'dl' or 'd' or 'l' - dehomogenization (linear)
        * 3 or 'fi' - initial failure indices and strength ratios
        * 4 or 'f' - (SwiftComp) initial failure strength
        * 5 or 'fe' - (SwiftComp) initial failure envelope
    smdim : int
        (SwiftComp) Dimension of the macroscopic structural model.
    aperiodic : bool
        (SwiftComp) If the structure gene is periodic.
    output_gmsh_format : bool
        (SwiftComp) If output dehomogenization results in Gmsh format
    reduced_integration : bool
        (SwiftComp) If reduced integration is used for certain elements.
    scrnout : bool, default True
        Switch of printing solver messages.
    logger : logging.Logger
        Logger object
    """
    logger.debug(f'local variables:\n{sutl.convertToPrettyString(locals())}')

    try:
        if solver.lower().startswith('v'):
            runVABS(solver, input_name, analysis, scrnout, timeout)

        elif solver.lower().startswith('s'):
            runSwiftComp(
                solver, input_name, analysis, smdim,
                aperiodic, output_gmsh_format, reduced_integration,
                scrnout, timeout
            )

    except:
        e = traceback.format_exc()
        logger.critical(e, exc_info=1)


# def solve(
#     sg_xml, analysis, ppcmd, solver, integrated=False,
#     aperiodic=False, output_gmsh_format=True, reduced_integration=False,
#     timeout=30, scrnout=True, logger=None, timer=None
#     ):
#     """Solve

#     Parameters
#     ----------
#     sg_xml : str
#         File name of SG design parameters (XML format).
#     analysis : str
#         Analysis to be carried out.

#         * h - homogenization
#         * d - dehomogenization/localization/recover
#         * f - initial failure strength
#         * fe - initial failure envelope
#         * fi - initial failure indices and strength ratios
#     ppcmd : str
#         Preprocessor command.
#     solver : str
#         Command of the solver.
#     integrated : bool, optional
#         Use integrated solver or not (standalone), by default False.
#     aperiodic : bool, optional
#         (SwiftComp) If the structure gene is periodic, by default False.
#     output_gmsh_format : bool, optional
#         (SwiftComp) If output dehomogenization results in Gmsh format, by default True
#     reduced_integration : bool, optional
#         (SwiftComp) If reduced integration is used for certain elements, by default False.
#     timeout : int, optional
#         Time to wait before stop, by default 30.
#     scrnout : bool, optional
#         Switch of printing solver messages, by default True.
#     logger : logging.Logger, optional
#         Logger object, by default None.

#     Returns
#     -------
#     various
#         Different analyses return different types of results.
#     """

#     if logger is None:
#         logger = mul.initLogger(__name__)

#     # t = mtime.Timer(logger=logger.info)

#     # Preprocess
#     logger.info('preprocessing...')

#     design = {'dim': 2}
#     smdim = 1

#     if timer:
#         timer.start()
#     sg_in = msp.buildSG(
#         sg_xml, design, smdim,
#         builder=ppcmd, analysis=analysis, solver=solver, integrated=integrated,
#         timeout=timeout, scrnout=scrnout, logger=logger
#     )
#     if timer:
#         timer.stop()


#     # Solve
#     if not integrated:
#         logger.info('running analysis...')
#         logger.debug('solver: ' + solver)
#         if timer:
#             timer.start()
#         run(
#             solver, sg_in, analysis, smdim,
#             aperiodic, output_gmsh_format, reduced_integration,
#             scrnout, logger=logger
#         )
#         if timer:
#             timer.stop()


#     # Parse results
#     logger.info('reading results...')

#     results = None

#     if timer:
#         timer.start()
    
#     if 'vabs' in solver.lower():
#         results = msi.readVABSOut(sg_in, analysis, scrnout, logger=logger)

#     elif 'swiftcomp' in solver.lower():
#         results = msi.readSCOut(sg_in, smdim, analysis, scrnout)

    
#     if timer:
#         timer.stop()
    
#     return results









def runVABS(command, input_name, analysis, scrnout=True, timeout=3600):
    """Run VABS.

    Parameters
    ----------
    command : str
        Command name of VABS
    input_name : str
        Name of the input file.
    analysis : {0, 1, 2, 3, '', 'h', 'dn', 'dl', 'd', 'l', 'fi'}
        Analysis to be carried out.

        * 0 or 'h' or '' - homogenization
        * 1 or 'dn' - dehomogenization (nonlinear)
        * 2 or 'dl' or 'd' or 'l' - dehomogenization (linear)
        * 3 or 'fi' - initial failure indices and strength ratios
    scrnout : bool, default True
        Switch of printing solver messages.
    logger : logging.Logger
        Logger object
    """

    # if logger is None:
    #     logger = mul.initLogger(__name__)

    try:
        cmd = [command, input_name]

        if analysis == 0 or analysis == 'h' or analysis == '':
            pass
        elif analysis == 1 or analysis == 'dn':
            cmd.append('1')
        elif analysis == 2 or analysis == 'dl' or analysis == 'd' or analysis == 'l':
            cmd.append('2')
        elif analysis == 3 or analysis == 'fi':
            cmd.append('3')

        logger.info(' '.join(cmd))

        sue.run(cmd, timeout)

        # if scrnout:
        #     sbp.call(cmd)
        # else:
        #     FNULL = open(os.devnull, 'w')
        #     sbp.call(cmd, stdout=FNULL, stderr=sbp.STDOUT)

    except:
        e = traceback.format_exc()
        logger.critical(e, exc_info=1)

    return









def runSwiftComp(
    command, input_name, analysis, smdim,
    aperiodic=False, output_gmsh_format=True, reduced_integration=False,
    scrnout=True, timeout=3600):
    """Run SwiftComp.

    Parameters
    ----------
    command : str
        Command name of SwiftComp
    input_name : str
        Name of the input file.
    analysis : {0, 2, 3, 4, 5, '', 'h', 'dl', 'd', 'l', 'fi', 'f', 'fe'}
        Analysis to be carried out.

        * 0 or 'h' or '' - homogenization
        * 2 or 'dl' or 'd' or 'l' - dehomogenization (linear)
        * 3 or 'fi' - initial failure indices and strength ratios
        * 4 or 'f' - initial failure strength
        * 5 or 'fe' - initial failure envelope
    smdim : int
        Dimension of the macroscopic structural model.
    aperiodic : bool
        If the structure gene is periodic.
    output_gmsh_format : bool
        If output dehomogenization results in Gmsh format
    reduced_integration : bool
        If reduced integration is used for certain elements.
    scrnout : bool, default True
        Switch of printing solver messages..
    logger : logging.Logger
        Logger object
    """

    # if logger is None:
    #     logger = mul.initLogger(__name__)

    try:
        cmd = [command, input_name]

        cmd.append(str(smdim) + 'D')

        arg = ''

        if analysis == 0 or analysis == 'h' or analysis == '':
            arg = 'H'
            if aperiodic:
                arg += 'A'
        elif analysis == 2 or analysis == 'dl' or analysis == 'd' or analysis == 'l':
            arg = 'L'
            if aperiodic:
                arg += 'A'
            if output_gmsh_format:
                arg += 'G'
        elif analysis == 3 or analysis == 'fi':
            arg = 'FI'
        elif analysis == 4 or analysis == 'f':
            arg = 'F'
        elif analysis == 5 or analysis == 'fe':
            arg = 'FE'



        cmd.append(arg)

        if reduced_integration:
            cmd.append('R')

        logger.info(' '.join(cmd))

        sue.run(cmd, timeout)

        # if scrnout:
        #     sbp.call(cmd)
        # else:
        #     FNULL = open(os.devnull, 'w')
        #     sbp.call(cmd, stdout=FNULL, stderr=sbp.STDOUT)

    except:
        e = traceback.format_exc()
        logger.critical(e, exc_info=1)

    return




